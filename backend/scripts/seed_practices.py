"""
seed_practices.py
=================
Управляемое наполнение тестового сервера расписанием утренних практик.

Что делает:
  - Создаёт служебных мастеров (telegram_id 10001..10011) и сеет от их имени
    практики из backend/scripts/seed_practices.json.
  - Создаёт/находит ТЕСТ-ЮЗЕРОВ (реальные telegram-аккаунты, ID задаёт оператор
    в секции test_users JSON) и наполняет им пользовательскую сторону: личные
    записи дневника (note/dream), исторические attended-брони на наши completed-
    практики, чек-ины и отзывы, будущую и отменённую брони. Этого хватает, чтобы
    в приложении был наполненный таймлайн-фид (~40 карточек) для тестирования.
  - Идемпотентно: повторный запуск не дублирует существующие записи
    (мастера/практики — по JSONB-маркеру data.seed.source == "seed_practices_v2";
    тест-юзеры — find-or-create по telegram_id, их данные — по естественным
    ключам и unique-констрейнтам).
  - Reset/clean сносят ТОЛЬКО свои данные. У тест-юзеров — реальных аккаунтов —
    удаляются ИСКЛЮЧИТЕЛЬНО наши seed-строки (пересечение user_id ∈ test_users
    AND practice_id ∈ наши практики; личные записи — по маркеру в DiaryEvent).
    Сами аккаунты тест-юзеров и их не-seed данные НЕ удаляются никогда.

Режимы:
  seed (по умолчанию)  -- досев. Существующее не трогает, недостающее создаёт.
  --reset              -- снос своих данных + пересев из JSON.
  --clean              -- только снос своих данных.
  promote-master       -- хирургически выдать ОДНОМУ реальному юзеру роль master
                          + verified-профиль из сценария promote_master (НЕ сеет
                          практики, НЕ сносит; маркер manual_master_grant вне
                          clean/reset). Идемпотентно/перезаписываемо.
  --dry-run            -- флаг к любому режиму. Показывает план без записи в БД.
  --yes                -- пропустить интерактивное подтверждение (для скриптинга).

Запуск:
  docker compose exec app python scripts/seed_practices.py
  docker compose exec app python scripts/seed_practices.py --reset
  docker compose exec app python scripts/seed_practices.py --clean
  docker compose exec app python scripts/seed_practices.py --reset --dry-run
  docker compose exec app python scripts/seed_practices.py --reset --yes
  docker compose exec app python scripts/seed_practices.py promote-master \
      --scenario 8457062539 --dry-run
  docker compose exec app python scripts/seed_practices.py promote-master \
      --scenario 8457062539 --yes

Источник данных: scripts/seed_practices.json (рядом с этим файлом).
Маркеры своих данных:
  - MasterProfile.data.seed = {"source": "seed_practices_v2", "key": "<slug>"}
  - Practice.data.seed       = {"source": "seed_practices_v2", "owner_tid": <tid>,
                                "key": "<slug>", "batch": "<iso>"}
  - User.credentials.seed    = {"source": "seed_practices_v2", "test_user_key": ...}
  - DiaryEvent.snapshot.seed = {"source": "seed_practices_v2", ...}  (личные записи)

Переиспользует scripts/seed.py: create_seed_booking (Booking+Purchase+ledger) и
project_seed_booking_events (проекция брони в фид-таймлайн с backdate).

FK-safe порядок DELETE — по образцу tests/helpers.py:full_cleanup_range.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# ── sys.path bootstrap ───────────────────────────────────────────────────────
# Кладём backend/scripts (для импорта соседнего seed.py) и backend (для app.*)
# в sys.path. backend/scripts — не пакет (нет __init__.py), поэтому seed.py
# импортируется как top-level модуль по имени файла. resolve() устойчив к ../.
_HERE = Path(__file__).resolve().parent          # backend/scripts
_BACKEND = _HERE.parent                           # backend
for _p in (_HERE, _BACKEND):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditLog
from app.core.config import settings
from app.core.database import dispose_engine, get_session_factory
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.bookings.service import recalculate_participants
from app.modules.diary.models import (
    Checkin,
    DiaryEntry,
    DiaryEvent,
    Feedback,
)
from app.modules.diary.projections import (
    project_booking_cancelled,
    project_booking_confirmed,
    upsert_checkin_event,
    upsert_entry_event,
    upsert_feedback_event,
)
from app.modules.masters.models import MasterProfile
from app.modules.masters.service import get_master_display_name
from app.modules.notifications.models import Notification, NotificationDelivery
from app.modules.payments.models import (
    CompanyLedger,
    MasterLedger,
    Payment,
    Purchase,
    UserLedger,
)
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.practices.schemas import CreatePracticeRequest
from app.modules.practices.service import create_practice as service_create_practice
from app.modules.promos.models import Promo
from app.modules.reports.models import Report
from app.modules.users.models import User, UserRole
from app.modules.waitlist.models import Waitlist
from app.modules.withdrawals.models import Withdrawal

# Соседний скрипт scripts/seed.py — переиспользуем его проверенные booking-хелперы
# (create_seed_booking: Booking + Purchase + двойная ledger-проводка с reason
# "seed:..."; project_seed_booking_events: проекция в DiaryEvent с backdate).
from seed import create_seed_booking, project_seed_booking_events  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Константы
# ─────────────────────────────────────────────────────────────────────────────

SEED_SOURCE = "seed_practices_v2"
TID_MIN = 10001
TID_MAX = 10012

# Marker for MasterProfiles attached to role-switch TESTERS (real accounts that
# may switch into the master role). MUST differ from SEED_SOURCE: cmd_clean
# deletes the User of every MasterProfile whose data.seed.source == SEED_SOURCE,
# and these profiles hang off REAL tester accounts we must NEVER delete. With a
# distinct source they are invisible to _collect_our_ids, so clean/reset leave
# the tester accounts (and these profiles) intact.
SEED_SOURCE_TESTER = "seed_role_switch_tester"

# Marker for MasterProfiles created by the `promote-master` command — a manual,
# surgical grant of the master role to ONE real account (e.g. the project owner).
# Distinct from SEED_SOURCE / SEED_SOURCE_TESTER so cmd_clean/_collect_our_ids
# NEVER sweep this live account on a reset/clean.
MANUAL_GRANT_SOURCE = "manual_master_grant"

# Valid role strings for the role-switch allow-list (mirrors UserRole).
_VALID_ROLE_VALUES = {r.value for r in UserRole}

# Synthetic participant pool (fake accounts) for master-side seeding: they book
# onto tester-owned practices so attendance/analytics have data. Fake range, so
# clean/reset DELETES these accounts entirely (unlike the real testers).
SYNTH_TID_MIN = 10101
SYNTH_TID_MAX = 10199

# Defaults for the per-tester "as_master" block (when as_master == true).
# Counts are clamped to the available participant pool at seed time.
TESTER_MASTER_DEFAULTS = {
    "practices": 10,            # own practices spread over ±2 weeks
    "participants_completed": 6,  # attendees per completed practice
    "noshow_completed": 1,        # of which marked no_show
    "checkins_completed": 4,      # attendees leaving a check-in (mood)
    "feedbacks_completed": 4,     # attendees leaving a feedback (rating)
    "participants_scheduled": 4,  # confirmed bookings per scheduled practice
}

# ── База-библиотека + сценарии ───────────────────────────────────────────────
# Контент (мастера/practice_templates/пулы текстов) — единый источник правды в
# базе-библиотеке. Сценарии (seed_scenarios/*.json) подключают её через ключ
# "extends" и выбирают из неё (masters_select), задают расписание/граничные
# практики/тест-юзеров. Сценарии СМЕНЯЮТ друг друга через --reset (общий маркер
# SEED_SOURCE => reset чистит ВСЁ наше и сеет выбранный сценарий), не сосуществуют.
BASE_DIR = Path(__file__).parent
SCENARIOS_DIR = BASE_DIR / "seed_scenarios"
DEFAULT_BASE = "seed_practices.json"   # база по умолчанию (если сценарий не задал extends)
DEFAULT_SCENARIO = "default"           # сценарий по умолчанию (без флага --scenario)

# ── Тест-юзеры (пользовательские данные) ─────────────────────────────────────
# Тест-юзеры — это РЕАЛЬНЫЕ telegram-аккаунты (ID задаёт оператор в JSON,
# роль любая). Скрипт находит-или-создаёт юзера по telegram_id, НЕ меняя его
# роль и не перетирая его существующие данные, и наполняет ему пользовательскую
# сторону (дневник, брони, чек-ины, отзывы), чтобы тестировать таймлайн-фид.
#
# Маркер «наш тест-юзер» — JSONB-ключ User.credentials.seed.source == SEED_SOURCE
# (User.data в этой кодовой базе НЕТ; единственный JSONB-сандбокс — credentials,
# где уже живёт onboarding_completed — мы его не трогаем).
#
# Маркер «наша личная запись дневника» — DiaryEvent.snapshot.seed.source, потому
# что у DiaryEntry своего JSONB-поля нет. Связанный DiaryEntry достаётся через
# DiaryEvent.source_id. Практико-привязанные события (booking/checkin/feedback/
# practice) при зачистке ловятся по practice_id ∈ наши seed-практики, маркер на
# них не обязателен.

# Дефолтные объёмы на одного тест-юзера (можно переопределить в JSON per-user).
# Подобраны так, чтобы лента была наглядно «живой» и её было что листать:
#   28 личных записей + 14 attended (×2 карточки) + 12 чек-инов + 12 отзывов
#   + 4 будущих + 2 отменённых (×2) ≈ 80+ элементов фида.
TEST_USER_DEFAULTS = {
    "diary_entries": 28,
    "attended_bookings": 14,
    "checkins": 12,
    "feedbacks": 12,
    "upcoming_bookings": 4,
    "cancelled_bookings": 2,
}

# mood/rating теперь Integer score 1..10 (миграция d5e6f7a8b9c0,
# CHECK BETWEEN 1 AND 10). Маппинг дискретных уровней в score совпадает
# с тем, что применил backend в seed.py: low/confused=2, mid/good=6,
# high/fire=9 (середины зон 1-3 / 4-7 / 8-10).
MOOD_SCORES = (2, 6, 9)    # low / mid / high
RATING_SCORES = (9, 6, 2)  # fire / good / confused

# Личные записи дневника (note/dream) живут в базе-библиотеке (секция
# diary_templates) и грузятся через load_source(). Пулы текстов чек-инов и
# отзывов — там же (checkin_comments / feedback_comments). Сидер получает их
# как аргументы (pools), а не из модульной константы.

# Ролевая логика граничных / now-anchored броней (seed_one_test_user, шаг 4.5).
# create_seed_booking сам ставит статус брони по статусу практики
# (scheduled/live -> confirmed, completed -> attended); ROLE_BOOKING задаёт лишь:
#   book          — бронировать ли практику вообще (live_unbooked -> нет);
#   outcome_status — для проекции карточки-итога в фид (attended / no_show);
#   to_noshow     — переключить бронь в no_show после создания.
ROLE_BOOKING: dict[str, tuple[bool, str | None, bool]] = {
    "checkin":       (True, None, False),        # confirmed, без чек-ина -> баннер check-in
    "upcoming":      (True, None, False),        # confirmed, будущая -> просто запись
    "live":          (True, None, False),        # confirmed+joined -> экран эфира
    "feedback":      (True, "attended", False),  # attended, без отзыва -> баннер feedback
    "attended":      (True, "attended", False),  # attended -> завершённая карточка
    "noshow":        (True, "no_show", True),    # attended -> флип no_show -> «Неявка»
    "live_unbooked": (False, None, False),       # НЕ бронируется (демо «нельзя записаться»)
}
BOOKABLE_BOUNDARY_ROLES = {r for r, (book, *_rest) in ROLE_BOOKING.items() if book}


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="seed_practices",
        description=(
            "Служебные мастера + расписание из JSON. "
            "Идемпотентно. Не трогает чужие данные."
        ),
    )
    p.add_argument(
        "command",
        nargs="?",
        default="seed",
        choices=("seed", "reset", "clean", "promote-master"),
        help="seed (default) | reset | clean | promote-master",
    )
    p.add_argument(
        "--reset", action="store_true",
        help="shorthand for `command=reset`",
    )
    p.add_argument(
        "--clean", action="store_true",
        help="shorthand for `command=clean`",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="показать план без записи в БД",
    )
    p.add_argument(
        "--yes", action="store_true",
        help="пропустить интерактивное подтверждение",
    )
    p.add_argument(
        "--scenario", default=DEFAULT_SCENARIO, metavar="NAME",
        help=f"имя сценария из seed_scenarios/NAME.json (по умолчанию '{DEFAULT_SCENARIO}')",
    )
    p.add_argument(
        "--source", default=None, metavar="PATH",
        help="явный путь к JSON-сценарию (перебивает --scenario)",
    )
    args = p.parse_args()
    if args.reset:
        args.command = "reset"
    if args.clean:
        args.command = "clean"
    return args


# ─────────────────────────────────────────────────────────────────────────────
# Загрузка JSON
# ─────────────────────────────────────────────────────────────────────────────

def _join_lines(value: list[str] | str | None) -> str | None:
    """JSON хранит многострочные тексты как массивы строк -> '\\n'.join."""
    if value is None:
        return None
    if isinstance(value, list):
        return "\n".join(value)
    return value


def expand_schedule(
    templates: list[dict], schedule: dict, now: datetime,
) -> list[dict]:
    """Разворачивает practice_templates по сетке schedule в конкретные практики.

    Для каждого дня в окне [-days_back; +days_forward] от «сегодня» (в
    schedule.timezone) и для каждого слота берётся следующий шаблон по кругу
    (round-robin) — это даёт разнообразие направлений/мастеров/времени суток.
    Прошлые дни используют slots_past (реже), сегодняшний и будущие —
    slots_future (плотнее).

    Статус определяется датой относительно now:
      end   <= now          -> completed
      start <= now < end    -> live
      start >  now          -> scheduled

    key практики стабилен (v2-{date}-{HHMM}-{template_key}) -> идемпотентно при
    повторном прогоне в тот же день. Возвращает список practice-dict в том же
    формате, что раньше читался из JSON-секции "practices" (downstream-конвейер
    не меняется).
    """
    tz = ZoneInfo(schedule["timezone"])
    tzname = schedule["timezone"]
    days_back = int(schedule["days_back"])
    days_forward = int(schedule["days_forward"])
    slots_past = schedule["slots_past"]
    slots_future = schedule["slots_future"]

    today = now.astimezone(tz).date()
    out: list[dict] = []
    rr = 0  # round-robin индекс по всему окну
    for day_offset in range(-days_back, days_forward + 1):
        day = today + timedelta(days=day_offset)
        slots = slots_past if day_offset < 0 else slots_future
        for slot in slots:
            hh, mm = (int(x) for x in slot.split(":"))
            start = datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz)
            tmpl = templates[rr % len(templates)]
            rr += 1
            dur = int(tmpl.get("duration_minutes", 60))
            end = start + timedelta(minutes=dur)
            if end <= now:
                status = "completed"
            elif start <= now < end:
                status = "live"
            else:
                status = "scheduled"
            key = f"v2-{day.isoformat()}-{slot.replace(':', '')}-{tmpl['key']}"
            out.append({
                **tmpl,
                "key": key,
                "template_key": tmpl["key"],
                "scheduled_at": start.isoformat(),
                "timezone": tzname,
                "status": status,
            })
    return out


def expand_boundary(
    boundary_templates: list[dict], schedule: dict, now: datetime,
) -> list[dict]:
    """Разворачивает boundary_practices относительно МОМЕНТА СЕВА (now).

    В отличие от слот-генератора (expand_schedule), привязка не к фикс-слотам, а
    к now + offset_minutes — чтобы граничные состояния (окно check-in / live /
    окно feedback / no_show / начавшаяся) гарантированно существовали сразу после
    сева, независимо от часа запуска. status берётся явно из шаблона; boundary_role
    управляет тем, как бронь вешается на тест-юзеров (seed_one_test_user, шаг 7).
    key стабилен (v2-boundary-*) -> идемпотентно; пересев формы — через --reset.
    """
    tz = ZoneInfo(schedule["timezone"])
    tzname = schedule["timezone"]
    out: list[dict] = []
    for t in boundary_templates:
        start = (now + timedelta(minutes=int(t["offset_minutes"]))).astimezone(tz)
        out.append({
            **t,
            "scheduled_at": start.isoformat(),
            "timezone": tzname,
            "boundary_role": t["role"],
        })
    return out


def expand_fixed_schedule(
    templates: list[dict], fixed: list[dict], now: datetime,
    default_zoom: str | None = None,
) -> list[dict]:
    """Разворачивает fixed_schedule — практики с АБСОЛЮТНОЙ датой/временем.

    В отличие от schedule (слот-генератор, относительно «сегодня») и
    boundary_practices (offset_minutes от now), эта секция привязывает практику к
    КОНКРЕТНОЙ дате/времени — для воспроизведения реального расписания продакта.

    Каждая запись ссылается на practice_templates по ключу (template), задаёт
    date (YYYY-MM-DD) + time (HH:MM) в своей timezone (по умолчанию
    Europe/Moscow) и опционально zoom_link (иначе default_zoom — общий на все).
    Длительность/направление/описание/теги берутся из шаблона как есть. Статус —
    от now (completed/live/scheduled). key стабилен:
    product-{date}-{HHMM}-{template_key} -> идемпотентно при повторном прогоне.
    """
    by_key = {t["key"]: t for t in templates}
    out: list[dict] = []
    for entry in fixed:
        tkey = entry["template"]
        tmpl = by_key.get(tkey)
        if tmpl is None:
            raise ValueError(
                f"fixed_schedule: неизвестный template '{tkey}' "
                f"(нет в practice_templates после masters_select)",
            )
        tzname = entry.get("timezone", "Europe/Moscow")
        tz = ZoneInfo(tzname)
        y, m, d = (int(x) for x in entry["date"].split("-"))
        hh, mm = (int(x) for x in entry["time"].split(":"))
        start = datetime(y, m, d, hh, mm, tzinfo=tz)
        dur = int(tmpl.get("duration_minutes", 60))
        end = start + timedelta(minutes=dur)
        if end <= now:
            status = "completed"
        elif start <= now < end:
            status = "live"
        else:
            status = "scheduled"
        key = f"product-{entry['date']}-{entry['time'].replace(':', '')}-{tkey}"
        out.append({
            **tmpl,
            "key": key,
            "template_key": tkey,
            # Optional per-entry title override: the product scenario names its
            # practices by the operator's exact genre labels, while the library
            # template keeps its own "marketed" title for other scenarios.
            "title": entry.get("title", tmpl.get("title")),
            "scheduled_at": start.isoformat(),
            "timezone": tzname,
            "status": status,
            "zoom_link": entry.get("zoom_link", default_zoom),
        })
    return out


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_source(scenario: str, explicit_source: str | None = None) -> dict:
    """Собирает итоговый источник: сценарий (seed_scenarios/NAME.json) поверх
    базы-библиотеки (extends). Контент (мастера/шаблоны/пулы) берётся из базы;
    сценарий переопределяет schedule / boundary_practices / test_users и может
    переопределить пулы. masters_select (int|list[str]) подрезает мастеров; под
    выбранных мастеров автоматически фильтруются practice_templates и
    boundary_practices (чтобы не остаться со ссылкой на отсутствующего мастера).
    """
    if explicit_source:
        scen_path = Path(explicit_source)
        if not scen_path.is_absolute():
            scen_path = BASE_DIR / explicit_source
    else:
        scen_path = SCENARIOS_DIR / f"{scenario}.json"
    scen = _read_json(scen_path)
    base = _read_json(BASE_DIR / scen.get("extends", DEFAULT_BASE))

    data = {
        "masters": list(base.get("masters", [])),
        "practice_templates": list(base.get("practice_templates", [])),
        "diary_templates": scen.get("diary_templates", base.get("diary_templates", [])),
        "checkin_comments": scen.get("checkin_comments", base.get("checkin_comments", [])),
        "feedback_comments": scen.get("feedback_comments", base.get("feedback_comments", [])),
        "schedule": scen.get("schedule") or base.get("schedule"),
        "boundary_practices": scen.get("boundary_practices", []),
        "fixed_schedule": scen.get("fixed_schedule", []),
        "fixed_zoom_link": scen.get("fixed_zoom_link"),
        "test_users": scen.get("test_users", []),
        "participant_pool": scen.get("participant_pool", []),
        "_scenario": scenario if not explicit_source else scen_path.name,
    }
    if not data["schedule"]:
        raise ValueError(
            f"сценарий '{data['_scenario']}': нет секции 'schedule' "
            f"(ни в сценарии, ни в базе)",
        )

    # Подрезка мастеров: int -> первые N; list -> по ключам.
    sel = scen.get("masters_select")
    if sel is not None:
        if isinstance(sel, int):
            data["masters"] = data["masters"][:sel]
        elif isinstance(sel, list):
            keyset = set(sel)
            chosen = [m for m in data["masters"] if m["key"] in keyset]
            missing = keyset - {m["key"] for m in chosen}
            if missing:
                raise ValueError(
                    f"сценарий '{data['_scenario']}': masters_select содержит "
                    f"неизвестные ключи {sorted(missing)}",
                )
            data["masters"] = chosen
        else:
            raise ValueError("masters_select должен быть int или list[str]")

    # Автофильтр шаблонов/граничных практик под выбранных мастеров.
    selected = {m["key"] for m in data["masters"]}
    data["practice_templates"] = [
        t for t in data["practice_templates"] if t["master"] in selected
    ]
    data["boundary_practices"] = [
        b for b in data["boundary_practices"] if b["master"] in selected
    ]
    return data


def load_source(scenario: str = DEFAULT_SCENARIO,
                explicit_source: str | None = None) -> dict:
    data = resolve_source(scenario, explicit_source)

    for m in data["masters"]:
        m["bio"] = _join_lines(m.get("bio"))

    # Расписание генерируется из шаблонов: practice_templates + schedule ->
    # конкретные практики (со scheduled_at/status). Кладём под ключ "practices",
    # чтобы остальной конвейер (cmd_seed, dry-run, тест-юзеры) работал без правок.
    # Граничные демо-практики (boundary_practices) добавляются в тот же список,
    # привязанные к now (см. expand_boundary). Один момент now на оба генератора.
    now = datetime.now(timezone.utc)
    data["practices"] = expand_schedule(
        data["practice_templates"], data["schedule"], now,
    )
    data["practices"] += expand_boundary(
        data.get("boundary_practices", []), data["schedule"], now,
    )
    data["practices"] += expand_fixed_schedule(
        data["practice_templates"], data.get("fixed_schedule", []), now,
        default_zoom=data.get("fixed_zoom_link"),
    )
    for p in data["practices"]:
        p["description"] = _join_lines(p.get("description"))
        # what_to_prepare / contraindications обычно строки, но на всякий случай:
        p["what_to_prepare"] = _join_lines(p.get("what_to_prepare"))
        p["contraindications"] = _join_lines(p.get("contraindications"))

    # Склейка multiline content у личных записей дневника (note/dream).
    for t in data.get("diary_templates", []):
        t["content"] = _join_lines(t.get("content"))

    return data


# ─────────────────────────────────────────────────────────────────────────────
# Подтверждение destructive
# ─────────────────────────────────────────────────────────────────────────────

def confirm_destructive(action: str) -> bool:
    print()
    print(f"!! Деструктивная операция: {action.upper()}")
    print(f"   Удалится всё, что принадлежит служебным мастерам с маркером")
    print(f"   data.seed.source == '{SEED_SOURCE}' (TID {TID_MIN}..{TID_MAX}).")
    print(f"   Это включает связанные bookings, purchases, ledger-записи и т.д.")
    print()
    response = input('   Введите "yes" для подтверждения: ').strip().lower()
    return response == "yes"


# ─────────────────────────────────────────────────────────────────────────────
# Поиск/создание служебного мастера
# ─────────────────────────────────────────────────────────────────────────────

async def _find_master_by_tid(
    session: AsyncSession, telegram_id: int,
) -> User | None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none()


def _build_master_profile_data(master_yaml: dict) -> dict:
    """Структура MasterProfile.data для служебного мастера."""
    return {
        "account": {
            "status": "verified",
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "verification": None,
            "rejections": [],
        },
        "profile": {
            "display_name": master_yaml["display_name"],
            "email": None,
            "phone": None,
            "bio": master_yaml.get("bio"),
            "methods": master_yaml.get("methods", []),
            "experience_years": None,
            "certifications": [],
        },
        "documents": [],
        "availability": {
            "is_accepting": True,   # !! именно is_accepting (см. masters/service.py:67)
            "note": None,
        },
        "settings": {
            "auto_confirm_bookings": True,
            "max_participants_default": 20,
        },
        "stats": {
            "total_practices": 0,
            "total_participants": 0,
            "avg_rating": None,
        },
        "seed": {
            "source": SEED_SOURCE,
            "key": master_yaml["key"],
        },
    }


async def ensure_master(
    session: AsyncSession, master_yaml: dict, dry_run: bool,
) -> tuple[User | None, str]:
    """Создаёт или возвращает существующего служебного мастера.

    Returns (user, action) где action ∈ {"created", "existing", "would-create"}.
    """
    existing = await _find_master_by_tid(session, master_yaml["telegram_id"])
    if existing:
        return existing, "existing"

    if dry_run:
        return None, "would-create"

    user = User(
        telegram_id=master_yaml["telegram_id"],
        first_name=master_yaml["first_name"],
        last_name=master_yaml.get("last_name"),
        role=UserRole.MASTER,
        is_active=True,
    )
    session.add(user)
    await session.flush()  # получаем user.id

    profile = MasterProfile(user_id=user.id)
    profile.set_jsonb("data", _build_master_profile_data(master_yaml))
    session.add(profile)
    await session.flush()

    return user, "created"


# ─────────────────────────────────────────────────────────────────────────────
# Поиск/создание практики
# ─────────────────────────────────────────────────────────────────────────────

async def _find_practice_by_key(
    session: AsyncSession, key: str,
) -> Practice | None:
    stmt = select(Practice).where(
        Practice.data["seed"]["key"].astext == key,
    )
    return (await session.execute(stmt)).scalar_one_or_none()


def _validate_practice_for_orm_insert(p: dict) -> None:
    """Ручная валидация для прямого ORM-insert (используется для прошлых практик,
    которые не пропускает Pydantic из-за scheduled_at_must_be_future).

    Дублирует существенную часть CreatePracticeRequest-валидаторов.
    """
    if p["practice_type"] not in settings.practice_allowed_types:
        raise ValueError(
            f"practice {p['key']}: practice_type='{p['practice_type']}' "
            f"not in {settings.practice_allowed_types}",
        )
    if p["direction"] not in settings.practice_allowed_directions:
        raise ValueError(
            f"practice {p['key']}: direction='{p['direction']}' "
            f"not in {settings.practice_allowed_directions}",
        )
    if p["difficulty"] not in settings.practice_allowed_difficulties:
        raise ValueError(
            f"practice {p['key']}: difficulty='{p['difficulty']}' "
            f"not in {settings.practice_allowed_difficulties}",
        )
    currency = p.get("currency", "eur")
    if currency not in settings.practice_allowed_currencies:
        raise ValueError(
            f"practice {p['key']}: currency='{currency}' "
            f"not in {settings.practice_allowed_currencies}",
        )

    title = p["title"]
    if not (1 <= len(title) <= settings.practice_title_max_length):
        raise ValueError(
            f"practice {p['key']}: title length {len(title)} "
            f"out of [1, {settings.practice_title_max_length}]",
        )
    for fld in ("description", "what_to_prepare", "contraindications"):
        v = p.get(fld)
        if v is not None and len(v) > settings.practice_description_max_length:
            raise ValueError(
                f"practice {p['key']}: {fld} length {len(v)} "
                f"exceeds {settings.practice_description_max_length}",
            )

    duration = p.get("duration_minutes", 60)
    if not (settings.practice_min_duration_minutes
            <= duration
            <= settings.practice_max_duration_minutes):
        raise ValueError(
            f"practice {p['key']}: duration_minutes={duration} "
            f"out of [{settings.practice_min_duration_minutes}, "
            f"{settings.practice_max_duration_minutes}]",
        )

    style = p.get("style")
    if style is not None:
        # Taxonomy v2 (2026-05-28): style is direction-conditional.
        by_dir = settings.practice_allowed_styles_by_direction
        allowed_for_dir = by_dir.get(p["direction"])
        if allowed_for_dir is None:
            raise ValueError(
                f"practice {p['key']}: direction='{p['direction']}' does not "
                f"admit a style; got '{style}'",
            )
        if style not in allowed_for_dir:
            raise ValueError(
                f"practice {p['key']}: style='{style}' for "
                f"direction='{p['direction']}' not in {allowed_for_dir}",
            )
        if len(style) > settings.practice_style_max_length:
            raise ValueError(
                f"practice {p['key']}: style length {len(style)} "
                f"exceeds {settings.practice_style_max_length}",
            )

    status = p.get("status", "scheduled")
    valid_statuses = {s.value for s in PracticeStatus}
    if status not in valid_statuses:
        raise ValueError(
            f"practice {p['key']}: status='{status}' "
            f"not in {sorted(valid_statuses)}",
        )


async def ensure_practice(
    session: AsyncSession,
    master_user: User,
    p_yaml: dict,
    dry_run: bool,
    batch_iso: str,
    *,
    force_orm: bool = False,
) -> tuple[Practice | None, str]:
    """Create-or-return a practice owned by master_user.

    force_orm=True forces the direct ORM-insert path for BOTH past and future
    practices (with manual validation), bypassing the service. Used for
    tester-owned practices: the testers' base role is USER (they switch up),
    so the master-only service path must not be taken for their future practices.
    """
    existing = await _find_practice_by_key(session, p_yaml["key"])
    if existing:
        return existing, "existing"

    if dry_run:
        return None, "would-create"

    scheduled_at_str = p_yaml["scheduled_at"]
    scheduled_at = datetime.fromisoformat(scheduled_at_str)
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
    is_future = scheduled_at > datetime.now(timezone.utc) and not force_orm

    target_status = p_yaml.get("status", "scheduled")
    target_status_valid = {s.value for s in PracticeStatus}
    if target_status not in target_status_valid:
        raise ValueError(
            f"practice {p_yaml['key']}: status='{target_status}' "
            f"not in {sorted(target_status_valid)}",
        )

    if is_future:
        # Будущая практика -- через сервис, Pydantic-валидаторы бесплатно.
        body = CreatePracticeRequest(
            practice_type=p_yaml["practice_type"],
            title=p_yaml["title"],
            description=p_yaml.get("description"),
            what_to_prepare=p_yaml.get("what_to_prepare"),
            contraindications=p_yaml.get("contraindications"),
            scheduled_at=scheduled_at,
            duration_minutes=p_yaml.get("duration_minutes", 60),
            timezone=p_yaml.get("timezone", "Europe/Moscow"),
            max_participants=p_yaml.get("max_participants"),
            zoom_link=p_yaml.get("zoom_link"),
            parent_practice_id=None,
            is_free=p_yaml.get("is_free", True),
            price_cents=p_yaml.get("price_cents", 0),
            currency=p_yaml.get("currency", "eur"),
            direction=p_yaml["direction"],
            difficulty=p_yaml["difficulty"],
            style=p_yaml.get("style"),
        )
        practice = await service_create_practice(master_user, body, session)
        await session.flush()
    else:
        # Прошлая практика -- прямой ORM-insert, минуя Pydantic
        # (scheduled_at_must_be_future блокирует прошлые даты).
        _validate_practice_for_orm_insert(p_yaml)
        practice = Practice(
            master_id=master_user.id,
            practice_type=p_yaml["practice_type"],
            title=p_yaml["title"],
            description=p_yaml.get("description"),
            what_to_prepare=p_yaml.get("what_to_prepare"),
            contraindications=p_yaml.get("contraindications"),
            scheduled_at=scheduled_at,
            duration_minutes=p_yaml.get("duration_minutes", 60),
            timezone=p_yaml.get("timezone", "Europe/Moscow"),
            max_participants=p_yaml.get("max_participants"),
            is_free=p_yaml.get("is_free", True),
            price_cents=p_yaml.get("price_cents", 0),
            currency=p_yaml.get("currency", "eur"),
            zoom_link=p_yaml.get("zoom_link"),
            parent_practice_id=None,
        )
        session.add(practice)
        await session.flush()

    # Маркер seed + taxonomy (для прямого ORM-insert) + статус.
    # Для будущих практик сервис уже положил {"taxonomy": {...}};
    # для прошлых -- data ещё пустая (server_default "{}").
    current_data = dict(practice.data) if practice.data else {}
    if "taxonomy" not in current_data:
        current_data["taxonomy"] = {
            "direction": p_yaml["direction"],
            "difficulty": p_yaml["difficulty"],
            "style": p_yaml.get("style"),
        }
    current_data["seed"] = {
        "source": SEED_SOURCE,
        "owner_tid": master_user.telegram_id,
        "key": p_yaml["key"],
        "batch": batch_iso,
    }
    practice.set_jsonb("data", current_data)

    # Статус: сервис всегда создаёт draft. Для всех остальных -- ставим вручную.
    if practice.status != target_status:
        practice.status = target_status

    return practice, "created"


# ─────────────────────────────────────────────────────────────────────────────
# SEED
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_seed(
    session: AsyncSession, source: dict, dry_run: bool,
) -> None:
    batch_iso = datetime.now(timezone.utc).isoformat()
    prefix = "[DRY-RUN] " if dry_run else ""

    print(f"\n=== SEED ===")
    print(f"Сценарий: {source.get('_scenario', '?')}")
    print(f"Мастеров в наборе: {len(source.get('masters', []))}")
    print(f"Batch:    {batch_iso}")
    print(f"{prefix}Мастера:")

    masters_by_key: dict[str, User] = {}
    for m in source["masters"]:
        user, action = await ensure_master(session, m, dry_run)
        marker = {"created": "+", "existing": "·", "would-create": "?"}[action]
        print(f"  {marker} {m['key']:<20s}  TID {m['telegram_id']}")
        if user:
            masters_by_key[m["key"]] = user

    print(f"\n{prefix}Практики:")
    # Собираем созданные/существующие Practice-объекты по статусу — они нужны
    # фазе тест-юзеров (attended → completed-практики, upcoming/cancelled →
    # scheduled-практики).
    completed_practices: list[Practice] = []
    scheduled_practices: list[Practice] = []
    # Граничные практики (boundary_role) идут в отдельную мапу role -> [практики]
    # (на одну роль может быть несколько практик — плотные сценарии). У них своя
    # ролевая логика броней (шаг 4.5 в seed_one_test_user), в общие пулы
    # attended/upcoming/cancelled они НЕ попадают.
    boundary_by_role: dict[str, list[Practice]] = {}
    for p in source["practices"]:
        master_user = masters_by_key.get(p["master"])
        if master_user is None:
            # В dry-run мастер может не существовать -- пометим как would-create.
            if dry_run:
                print(f"  ? {p['key']}  (мастер '{p['master']}' был бы создан)")
                continue
            raise RuntimeError(
                f"practice {p['key']}: мастер '{p['master']}' не найден",
            )
        practice, action = await ensure_practice(
            session, master_user, p, dry_run, batch_iso,
        )
        marker = {"created": "+", "existing": "·", "would-create": "?"}[action]
        print(f"  {marker} {p['key']}")
        if practice is not None:
            role = p.get("boundary_role")
            if role:
                boundary_by_role.setdefault(role, []).append(practice)
            elif p.get("status") == "completed":
                completed_practices.append(practice)
            elif p.get("status") == "scheduled":
                scheduled_practices.append(practice)

    # ── Тест-юзеры: пользовательские данные ──────────────────────────────────
    test_users = source.get("test_users", [])
    if test_users:
        # Счётчики из JSON — для честной оценки в dry-run (там Practice-объекты
        # не создаются, а план хочется показать по реальному числу практик).
        src_completed = sum(
            1 for p in source["practices"] if p.get("status") == "completed"
        )
        src_scheduled = sum(
            1 for p in source["practices"] if p.get("status") == "scheduled"
        )
        # Бронируемые граничные роли (live_unbooked не в счёт — её не бронируем).
        src_boundary = sum(
            1 for p in source["practices"]
            if p.get("boundary_role") in BOOKABLE_BOUNDARY_ROLES
        )
        pools = {
            "diary": source.get("diary_templates", []),
            "checkin": source.get("checkin_comments", []),
            "feedback": source.get("feedback_comments", []),
        }
        await cmd_seed_test_users(
            session,
            test_users,
            completed_practices,
            scheduled_practices,
            batch_iso,
            dry_run,
            pools,
            boundary_by_role,
            src_completed=src_completed,
            src_scheduled=src_scheduled,
            src_boundary=src_boundary,
        )

    # ── Мастер-сторона: тестеры — владельцы своих практик (as_master) ────────
    master_testers = [tu for tu in test_users if tu.get("as_master")]
    if master_testers:
        now_m = datetime.now(timezone.utc)
        templates_m = source.get("practice_templates", [])
        m_pools = {
            "checkin": source.get("checkin_comments", []),
            "feedback": source.get("feedback_comments", []),
        }
        print(f"\n{prefix}Тестеры-мастера (свои практики + участники):")
        participants = await ensure_participant_pool(
            session, source.get("participant_pool", []), dry_run,
        )
        for tu in master_testers:
            tester = await _find_user_by_tid(session, tu["telegram_id"])
            if tester is None:
                print(f"  ? {tu.get('key', tu['telegram_id'])} (как мастер; "
                      f"аккаунт ещё не создан)")
                continue
            am = tu.get("as_master")
            overrides = am if isinstance(am, dict) else {}
            cfg_m = {**TESTER_MASTER_DEFAULTS, **overrides}
            mstats = await seed_tester_as_master(
                session, tester, cfg_m, participants, templates_m,
                m_pools, batch_iso, now_m, dry_run,
            )
            print(
                f"  + {tu.get('key', tu['telegram_id'])}: "
                f"практик={mstats['practices']}, "
                f"участников={mstats['participants']}, "
                f"чек-ины={mstats['checkins']}, отзывы={mstats['feedbacks']}, "
                f"no_show={mstats['noshow']}"
            )

    if not dry_run:
        await session.commit()
        print("\nSeed завершён, изменения зафиксированы.")
    else:
        print("\n[DRY-RUN] Изменения в БД НЕ зафиксированы.")


# ─────────────────────────────────────────────────────────────────────────────
# TEST USERS — пользовательские данные (дневник, брони, чек-ины, отзывы)
# ─────────────────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _backdate(scheduled_at: datetime, delta, now: datetime) -> datetime:
    """occurred_at для исторических событий: момент относительно практики,
    но не позже now (карточка в фиде не должна оказаться в будущем).
    Страховка: если scheduled_at пришёл naive — трактуем как UTC."""
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
    return min(scheduled_at + delta, now)


def _stamp_event_seed(ev: DiaryEvent, *, owner_tid: int | None, key: str,
                      batch_iso: str) -> None:
    """Кладёт маркер в DiaryEvent.snapshot.seed — ОБЯЗАТЕЛЬНО после project_*/
    upsert_*_event (они полностью перезаписывают snapshot, маркер до них сотрётся).
    Для личных записей это единственная зацепка зачистки (у DiaryEntry своего
    JSONB нет); связанный DiaryEntry достаётся через ev.source_id."""
    if ev is None:
        return
    snap = dict(ev.snapshot or {})
    snap["seed"] = {
        "source": SEED_SOURCE,
        "owner_tid": owner_tid,
        "key": key,
        "batch": batch_iso,
    }
    ev.set_jsonb("snapshot", snap)


async def _find_user_by_tid(session: AsyncSession, telegram_id: int) -> User | None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def _has_any_booking(
    session: AsyncSession, user_id, practice_id,
) -> bool:
    """Любая бронь (вкл. cancelled) этого юзера на эту практику.
    Нужно для идемпотентности cancelled-сценария: create_seed_booking считает
    cancelled-бронь «неактивной» и на повторном прогоне создал бы дубль."""
    stmt = select(Booking.id).where(
        Booking.user_id == user_id,
        Booking.practice_id == practice_id,
    ).limit(1)
    return (await session.execute(stmt)).scalar_one_or_none() is not None


# Статусы брони, занимающие место (для клэмпа вместимости при посеве).
# Бэкенд при бронировании режет по active-статусам, а current_participants
# (то, что показывает «N/M мест») считает CONFIRMED+ATTENDED — берём
# объединение «занимающих» статусов. cancelled/no_show место не держат.
_SEAT_BOOKING_STATUSES = (
    BookingStatus.PENDING.value,
    BookingStatus.CONFIRMED.value,
    BookingStatus.ATTENDED.value,
)


async def _practice_has_room(
    session: AsyncSession, practice: Practice,
) -> bool:
    """True, если у практики есть свободное место (или вместимость безлимитна).

    Считает ЖИВЫМ COUNT по занимающим место броням (поле
    practice.current_participants во время сева ещё не пересчитано — оно
    обновляется в самом конце). Не даёт посеву навесить активных броней сверх
    max_participants: иначе на индивидуальных сессиях (1 место) получался
    артефакт вида «6/1 мест». Живой пользователь так переполнить не может —
    это страховка именно для прямой вставки сидом мимо API."""
    if practice.max_participants is None:
        return True
    stmt = select(func.count(Booking.id)).where(
        Booking.practice_id == practice.id,
        Booking.status.in_(_SEAT_BOOKING_STATUSES),
    )
    taken = (await session.execute(stmt)).scalar_one()
    return taken < practice.max_participants


def _tester_allowed_roles(tu: dict) -> list[str] | None:
    """Normalize a test user's role-switch allow-list from JSON.

    Reads tu["allowed_roles"], keeps only valid role strings (user/master/
    admin) preserving order, drops duplicates. Returns None when the field is
    absent or yields nothing — meaning "ordinary test user, no role switch".
    """
    raw = tu.get("allowed_roles")
    if not isinstance(raw, list):
        return None
    roles: list[str] = []
    for r in raw:
        if r in _VALID_ROLE_VALUES and r not in roles:
            roles.append(r)
    return roles or None


def _build_tester_master_profile_data(tu: dict) -> dict:
    """MasterProfile.data for a role-switch TESTER (verified, minimal).

    Distinct seed marker (SEED_SOURCE_TESTER) so cmd_clean never mistakes the
    tester for a service master and deletes their real account.
    """
    name = tu.get("first_name") or f"Tester {tu['telegram_id']}"
    return {
        "account": {
            "status": "verified",
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "verification": None,
            "rejections": [],
        },
        "profile": {
            "display_name": name,
            "email": None,
            "phone": None,
            "bio": None,
            "methods": [],
            "experience_years": None,
            "certifications": [],
        },
        "documents": [],
        "availability": {"is_accepting": True, "note": None},
        "settings": {
            "auto_confirm_bookings": True,
            "max_participants_default": 20,
        },
        "stats": {
            "total_practices": 0,
            "total_participants": 0,
            "avg_rating": None,
        },
        "seed": {
            "source": SEED_SOURCE_TESTER,
            "test_user_key": tu.get("key"),
        },
    }


async def _ensure_tester_master_profile(
    session: AsyncSession, user: User, tu: dict,
) -> bool:
    """Ensure a tester who may switch into master has a verified profile.

    Idempotent: skips if any MasterProfile already exists for the user.
    Returns True if a profile was created.
    """
    existing = (await session.execute(
        select(MasterProfile).where(MasterProfile.user_id == user.id),
    )).scalar_one_or_none()
    if existing:
        return False
    profile = MasterProfile(user_id=user.id)
    profile.set_jsonb("data", _build_tester_master_profile_data(tu))
    session.add(profile)
    await session.flush()
    return True


async def ensure_test_user(
    session: AsyncSession, tu: dict, dry_run: bool,
) -> tuple[User | None, str]:
    """find-or-create тест-юзера по telegram_id.

    Обычный тест-юзер: если уже есть — НЕ меняем роль и НЕ перетираем данные,
    только добавляем маркер credentials.seed; если нет — создаём с role=USER.

    Role-switch ТЕСТЕР (в JSON задан allowed_roles): дополнительно прописываем
    credentials.role_switch.allowed_roles, держим базовую роль = USER (свитч
    идёт вверх от неё), и если в наборе есть master — создаём ему verified
    MasterProfile (с отдельным маркером SEED_SOURCE_TESTER, чтобы clean не
    удалил реальный аккаунт). Изменение роли допускаем ТОЛЬКО для наших
    тестеров (allowed_roles задан) — чужие аккаунты не трогаем.

    Возвращает (user, action), action ∈ {created, existing, marked, would-create}.
    """
    allowed_roles = _tester_allowed_roles(tu)
    existing = await _find_user_by_tid(session, tu["telegram_id"])

    if existing:
        if dry_run:
            return existing, "existing"
        changed = False
        creds = dict(existing.credentials or {})
        if creds.get("seed", {}).get("source") != SEED_SOURCE:
            creds["seed"] = {
                "source": SEED_SOURCE,
                "test_user_key": tu.get("key"),
                "first_seeded_at": _now().isoformat(),
            }
            changed = True
        if allowed_roles is not None and (
            creds.get("role_switch", {}).get("allowed_roles") != allowed_roles
        ):
            creds["role_switch"] = {"allowed_roles": allowed_roles}
            changed = True
        if changed:
            existing.set_jsonb("credentials", creds)
        # Testers get a deterministic base role = USER on (re)seed; switch up
        # from there. Only OUR testers (allowed_roles set) — never touch others.
        if allowed_roles is not None and existing.role != UserRole.USER:
            existing.role = UserRole.USER
            changed = True
        if allowed_roles and "master" in allowed_roles:
            if await _ensure_tester_master_profile(session, existing, tu):
                changed = True
        if changed:
            await session.flush()
            return existing, "marked"
        return existing, "existing"

    if dry_run:
        return None, "would-create"

    creds = {
        "onboarding_completed": True,
        "seed": {
            "source": SEED_SOURCE,
            "test_user_key": tu.get("key"),
            "first_seeded_at": _now().isoformat(),
        },
    }
    if allowed_roles is not None:
        creds["role_switch"] = {"allowed_roles": allowed_roles}

    user = User(
        telegram_id=tu["telegram_id"],
        first_name=tu.get("first_name") or f"Tester {tu['telegram_id']}",
        last_name=tu.get("last_name"),
        role=UserRole.USER,
        is_active=True,
    )
    user.set_jsonb("credentials", creds)
    if tu.get("language"):
        # language — опциональное поле; ставим только если модель его принимает.
        if hasattr(user, "language"):
            user.language = tu["language"]
    session.add(user)
    await session.flush()

    if allowed_roles and "master" in allowed_roles:
        await _ensure_tester_master_profile(session, user, tu)

    return user, "created"


async def create_v2_diary_entries(
    session: AsyncSession, user: User, count: int, batch_iso: str,
    templates: list[dict],
) -> int:
    """Сеет личные записи дневника (note/dream) тест-юзеру. Backdate через
    entry.created_at ДО проекции, маркер — в snapshot.seed связанного DiaryEvent.
    Идемпотентно по (user_id, title, entry_type). templates — из JSON
    (source.diary_templates)."""
    created = 0
    now = _now()
    for tmpl in templates[:count]:
        # Идемпотентность.
        dup = (await session.execute(
            select(DiaryEntry.id).where(
                DiaryEntry.user_id == user.id,
                DiaryEntry.title == tmpl["title"],
                DiaryEntry.entry_type == tmpl["entry_type"],
            ).limit(1),
        )).scalar_one_or_none()
        if dup is not None:
            continue

        entry = DiaryEntry(
            user_id=user.id,
            practice_id=None,
            entry_type=tmpl["entry_type"],
            practice_phase=tmpl.get("practice_phase"),
            title=tmpl["title"],
            content=tmpl["content"],
            mood=tmpl.get("mood"),
        )
        session.add(entry)
        # Backdate: occurred_at события = entry.created_at (см. projections).
        entry.created_at = now - timedelta(
            days=tmpl["offset_days"], hours=(tmpl["offset_days"] % 5),
        )
        await session.flush()

        ev = await upsert_entry_event(session, entry=entry)
        _stamp_event_seed(
            ev, owner_tid=user.telegram_id, key=f"diary:{tmpl['key']}",
            batch_iso=batch_iso,
        )
        created += 1
    return created


async def _seed_checkin(
    session: AsyncSession, user: User, practice: Practice, booking: Booking,
    master_name: str | None, batch_iso: str, idx: int, comments: list[str],
) -> bool:
    """Исторический pre-чек-ин ORM-insert'ом + ручная проекция в фид.
    Идемпотентно по UniqueConstraint(booking_id, check_type='pre').
    comments — пул текстов из JSON (source.checkin_comments)."""
    dup = (await session.execute(
        select(Checkin.id).where(
            Checkin.booking_id == booking.id,
            Checkin.check_type == "pre",
        ).limit(1),
    )).scalar_one_or_none()
    if dup is not None:
        return False

    now = _now()
    ck = Checkin(
        practice_id=practice.id,
        user_id=user.id,
        booking_id=booking.id,
        mood=MOOD_SCORES[idx % len(MOOD_SCORES)],
        comment=(comments[idx % len(comments)] if comments and idx % 2 == 0 else None),
        check_type="pre",
    )
    session.add(ck)
    ck.created_at = _backdate(
        practice.scheduled_at - timedelta(minutes=20), timedelta(0), now,
    )
    await session.flush()

    ev = await upsert_checkin_event(
        session, checkin=ck, practice=practice, master_name=master_name,
    )
    _stamp_event_seed(
        ev, owner_tid=user.telegram_id, key=f"checkin:{practice.id}",
        batch_iso=batch_iso,
    )
    return True


async def _seed_feedback(
    session: AsyncSession, user: User, practice: Practice, booking: Booking,
    master_name: str | None, batch_iso: str, idx: int, comments: list[str],
) -> bool:
    """Исторический отзыв ORM-insert'ом + ручная проекция в фид.
    Идемпотентно по UniqueConstraint(practice_id, user_id).
    comments — пул текстов из JSON (source.feedback_comments)."""
    dup = (await session.execute(
        select(Feedback.id).where(
            Feedback.practice_id == practice.id,
            Feedback.user_id == user.id,
        ).limit(1),
    )).scalar_one_or_none()
    if dup is not None:
        return False

    now = _now()
    fb = Feedback(
        practice_id=practice.id,
        user_id=user.id,
        booking_id=booking.id,
        rating=RATING_SCORES[idx % len(RATING_SCORES)],
        comment=(comments[idx % len(comments)] if comments else None),
    )
    session.add(fb)
    dur = practice.duration_minutes or 60
    fb.created_at = _backdate(
        practice.scheduled_at + timedelta(minutes=dur + 90), timedelta(0), now,
    )
    await session.flush()

    ev = await upsert_feedback_event(
        session, feedback=fb, practice=practice, master_name=master_name,
    )
    _stamp_event_seed(
        ev, owner_tid=user.telegram_id, key=f"feedback:{practice.id}",
        batch_iso=batch_iso,
    )
    return True


async def seed_one_test_user(
    session: AsyncSession,
    user: User,
    cfg: dict,
    completed: list[Practice],
    scheduled: list[Practice],
    batch_iso: str,
    pools: dict,
    boundary: dict,
) -> dict:
    """Наполняет одного тест-юзера. Возвращает счётчики для лога."""
    n_attended = min(cfg["attended_bookings"], len(completed))
    n_checkins = min(cfg["checkins"], n_attended)
    n_feedbacks = min(cfg["feedbacks"], n_attended)
    n_upcoming = min(cfg["upcoming_bookings"], len(scheduled))
    # Отменённую вешаем на scheduled-практику, не занятую upcoming.
    cancel_pool = scheduled[n_upcoming:]
    n_cancelled = min(cfg["cancelled_bookings"], len(cancel_pool))

    stats = {"diary": 0, "attended": 0, "checkins": 0,
             "feedbacks": 0, "upcoming": 0, "cancelled": 0, "boundary": 0}
    touched_practice_ids: set = set()

    # 1. Исторические attended-брони (+ confirmed/outcome события) на completed.
    attended_bookings: list[tuple[Practice, Booking]] = []
    for practice in completed[:n_attended]:
        if not await _practice_has_room(session, practice):
            continue  # вместимость исчерпана — не переполняем места
        booking = await create_seed_booking(session, user, practice)
        if booking is None:
            continue  # уже существует (идемпотентность) либо юзер == мастер
        await project_seed_booking_events(
            session, booking, practice, outcome_status="attended",
        )
        attended_bookings.append((practice, booking))
        touched_practice_ids.add(practice.id)
        stats["attended"] += 1

    # 2. Чек-ины и отзывы на части attended-броней.
    for i, (practice, booking) in enumerate(attended_bookings):
        master_name = await get_master_display_name(practice.master_id, session)
        if i < n_checkins:
            if await _seed_checkin(session, user, practice, booking,
                                   master_name, batch_iso, i, pools["checkin"]):
                stats["checkins"] += 1
        if i < n_feedbacks:
            if await _seed_feedback(session, user, practice, booking,
                                    master_name, batch_iso, i, pools["feedback"]):
                stats["feedbacks"] += 1

    # 3. Будущие confirmed-брони на scheduled-практики.
    for practice in scheduled[:n_upcoming]:
        if not await _practice_has_room(session, practice):
            continue  # вместимость исчерпана — не переполняем места
        booking = await create_seed_booking(session, user, practice)
        if booking is None:
            continue
        await project_seed_booking_events(session, booking, practice)
        touched_practice_ids.add(practice.id)
        stats["upcoming"] += 1

    # 4. Отменённая бронь: confirmed → CANCELLED + две карточки в фиде.
    for practice in cancel_pool[:n_cancelled]:
        if await _has_any_booking(session, user.id, practice.id):
            continue  # идемпотентность
        booking = await create_seed_booking(session, user, practice)
        if booking is None:
            continue
        now = _now()
        cancelled_at = _backdate(
            practice.scheduled_at - timedelta(days=1), timedelta(0), now,
        )
        booking.status = BookingStatus.CANCELLED.value
        booking.cancelled_at = cancelled_at
        await session.flush()
        master_name = await get_master_display_name(practice.master_id, session)
        ev_c = await project_booking_confirmed(
            session, booking=booking, practice=practice,
            master_name=master_name,
            occurred_at=cancelled_at - timedelta(days=1),
        )
        _stamp_event_seed(ev_c, owner_tid=user.telegram_id,
                          key=f"booking_confirmed:{booking.id}",
                          batch_iso=batch_iso)
        ev_x = await project_booking_cancelled(
            session, booking=booking, practice=practice,
            master_name=master_name, occurred_at=cancelled_at,
        )
        _stamp_event_seed(ev_x, owner_tid=user.telegram_id,
                          key=f"booking_cancelled:{booking.id}",
                          batch_iso=batch_iso)
        touched_practice_ids.add(practice.id)
        stats["cancelled"] += 1

    # 4.5. Граничные / now-anchored брони (boundary). На одну роль может быть
    # несколько практик (плотные сценарии типа super-active). Поведение брони —
    # по ROLE_BOOKING. create_seed_booking сам выставляет статус по статусу
    # практики (scheduled/live→confirmed[+joined], completed→attended). Баннеры
    # check-in/feedback показываются только если действие НЕ преднаполнено —
    # поэтому чек-ин/отзыв тут НЕ сеем. live_unbooked не бронируется.
    for role, practices in boundary.items():
        book, outcome, to_noshow = ROLE_BOOKING.get(role, (True, None, False))
        if not book:
            continue
        for practice in practices:
            if await _has_any_booking(session, user.id, practice.id):
                continue  # идемпотентность
            if not await _practice_has_room(session, practice):
                continue  # вместимость исчерпана — не переполняем места
            booking = await create_seed_booking(session, user, practice)
            if booking is None:
                continue
            if to_noshow:
                booking.status = BookingStatus.NO_SHOW.value
                booking.joined_at = None
                booking.left_at = None
                await session.flush()
            await project_seed_booking_events(
                session, booking, practice, outcome_status=outcome,
            )
            touched_practice_ids.add(practice.id)
            stats["boundary"] += 1

    # 5. Личные записи дневника.
    stats["diary"] = await create_v2_diary_entries(
        session, user, cfg["diary_entries"], batch_iso, pools["diary"],
    )

    # 6. Пересчёт участников по затронутым практикам (COUNT-based, идемпотентно).
    for pid in touched_practice_ids:
        await recalculate_participants(pid, session)

    return stats


# ─────────────────────────────────────────────────────────────────────────────
# MASTER-SIDE SEEDING — тестеры-владельцы практик + синтетические участники
# ─────────────────────────────────────────────────────────────────────────────

async def ensure_participant_pool(
    session: AsyncSession, pool_yaml: list[dict], dry_run: bool,
) -> list[User]:
    """find-or-create синтетических участников (фейк-аккаунты, TID 10101+).

    Маркер credentials.seed = {source, synthetic: True}. synthetic:True отличает
    их от реальных тест-юзеров: при clean/reset эти аккаунты УДАЛЯЮТСЯ целиком
    (каскад по user_id снесёт их брони/чек-ины/фидбеки/события), тогда как
    реальные тестеры сохраняются.
    """
    users: list[User] = []
    for p in pool_yaml:
        tid = p["telegram_id"]
        existing = await _find_user_by_tid(session, tid)
        if existing:
            users.append(existing)
            continue
        if dry_run:
            continue
        user = User(
            telegram_id=tid,
            first_name=p.get("first_name") or f"Participant {tid}",
            last_name=p.get("last_name"),
            role=UserRole.USER,
            is_active=True,
        )
        user.set_jsonb("credentials", {
            "onboarding_completed": True,
            "seed": {
                "source": SEED_SOURCE,
                "synthetic": True,
                "participant_key": p.get("key"),
            },
        })
        session.add(user)
        await session.flush()
        users.append(user)
    return users


def _build_tester_practice_dicts(
    tester: User, templates: list[dict], now: datetime, count: int,
) -> list[dict]:
    """Строит practice-dict'ы, принадлежащие тестеру, на ±2 недели.

    Микс completed (прошлое) + один live (now-10м) + scheduled (будущее). Контент
    из practice_templates (round-robin, сдвиг по TID -> у тестеров разные наборы).
    Статус по времени. key стабилен (mt-{tid}-{date}-{HHMM}-{tkey}) -> идемпотентно.
    """
    tz = ZoneInfo("Europe/Moscow")
    # Дни относительно сегодня: половина в прошлом (completed), половина в будущем.
    day_offsets = [-12, -10, -8, -6, -4, -2, 3, 6, 9, 12, 14]
    slot_hours = [10, 18]
    rr = (tester.telegram_id or 0)
    out: list[dict] = []

    def _mk(tmpl: dict, start: datetime, status: str, key: str) -> dict:
        return {
            **tmpl,
            "key": key,
            "template_key": tmpl["key"],
            "scheduled_at": start.isoformat(),
            "timezone": "Europe/Moscow",
            "status": status,
            "description": _join_lines(tmpl.get("description")),
            "what_to_prepare": _join_lines(tmpl.get("what_to_prepare")),
            "contraindications": _join_lines(tmpl.get("contraindications")),
        }

    # Одна live-практика (now - 10 минут) — всегда первой.
    live_tmpl = templates[rr % len(templates)]
    live_start = (now - timedelta(minutes=10)).astimezone(tz)
    out.append(_mk(
        live_tmpl, live_start, "live",
        f"mt-{tester.telegram_id}-live-{live_tmpl['key']}",
    ))

    for i, doff in enumerate(day_offsets[: max(0, count - 1)]):
        tmpl = templates[(rr + i + 1) % len(templates)]
        day = (now.astimezone(tz) + timedelta(days=doff)).date()
        hh = slot_hours[i % len(slot_hours)]
        start = datetime(day.year, day.month, day.day, hh, 0, tzinfo=tz)
        dur = int(tmpl.get("duration_minutes", 60))
        end = start + timedelta(minutes=dur)
        if end <= now:
            status = "completed"
        elif start <= now < end:
            status = "live"
        else:
            status = "scheduled"
        key = f"mt-{tester.telegram_id}-{day.isoformat()}-{hh:02d}00-{tmpl['key']}"
        out.append(_mk(tmpl, start, status, key))
    return out


async def seed_tester_as_master(
    session: AsyncSession,
    tester: User,
    cfg_m: dict,
    participants: list[User],
    templates: list[dict],
    pools: dict,
    batch_iso: str,
    now: datetime,
    dry_run: bool,
) -> dict:
    """Сеет практики, принадлежащие тестеру (мастер-сторона), + участников.

    completed -> участники attended (часть no_show) + чек-ины/фидбеки (для
    Аналитики/Посещаемости); scheduled/live -> участники confirmed. Брони делают
    СИНТЕТИКИ (project_seed_booking_events для них НЕ зовём — их фид не нужен;
    мастеру важны строки Booking/Checkin/Feedback). recalculate_participants в
    конце по каждой практике.
    """
    stats = {"practices": 0, "participants": 0, "checkins": 0,
             "feedbacks": 0, "noshow": 0}
    if dry_run:
        stats["practices"] = cfg_m["practices"]
        return stats
    if not templates:
        return stats

    p_dicts = _build_tester_practice_dicts(
        tester, templates, now, cfg_m["practices"],
    )
    for p_yaml in p_dicts:
        practice, _action = await ensure_practice(
            session, tester, p_yaml, dry_run, batch_iso, force_orm=True,
        )
        if practice is None:
            continue
        stats["practices"] += 1
        status = p_yaml["status"]

        if status == "completed":
            n_part = min(cfg_m["participants_completed"], len(participants))
            n_noshow = min(cfg_m["noshow_completed"], n_part)
            master_name = await get_master_display_name(practice.master_id, session)
            attended: list[tuple[User, Booking]] = []
            for j, part in enumerate(participants[:n_part]):
                if not await _practice_has_room(session, practice):
                    break
                booking = await create_seed_booking(session, part, practice)
                if booking is None:
                    continue
                stats["participants"] += 1
                if j < n_noshow:
                    booking.status = BookingStatus.NO_SHOW.value
                    booking.joined_at = None
                    booking.left_at = None
                    await session.flush()
                    stats["noshow"] += 1
                else:
                    attended.append((part, booking))
            for k, (part, booking) in enumerate(attended):
                if k < cfg_m["checkins_completed"]:
                    if await _seed_checkin(session, part, practice, booking,
                                           master_name, batch_iso, k,
                                           pools["checkin"]):
                        stats["checkins"] += 1
                if k < cfg_m["feedbacks_completed"]:
                    if await _seed_feedback(session, part, practice, booking,
                                            master_name, batch_iso, k,
                                            pools["feedback"]):
                        stats["feedbacks"] += 1
        else:
            # scheduled / live -> confirmed-брони участников.
            n_part = min(cfg_m["participants_scheduled"], len(participants))
            for part in participants[:n_part]:
                if not await _practice_has_room(session, practice):
                    break
                booking = await create_seed_booking(session, part, practice)
                if booking is None:
                    continue
                stats["participants"] += 1

        await recalculate_participants(practice.id, session)

    return stats


async def cmd_seed_test_users(
    session: AsyncSession,
    test_users: list[dict],
    completed: list[Practice],
    scheduled: list[Practice],
    batch_iso: str,
    dry_run: bool,
    pools: dict,
    boundary: dict,
    *,
    src_completed: int = 0,
    src_scheduled: int = 0,
    src_boundary: int = 0,
) -> None:
    prefix = "[DRY-RUN] " if dry_run else ""
    print(f"\n{prefix}Тест-юзеры (пользовательские данные):")

    for tu in test_users:
        if not tu.get("telegram_id"):
            print(f"  ! пропуск: у записи '{tu.get('key', '?')}' "
                  f"не задан telegram_id (впиши реальный TG-id в JSON)")
            continue

        cfg = {**TEST_USER_DEFAULTS, **{
            k: tu[k] for k in TEST_USER_DEFAULTS if k in tu
        }}

        user, action = await ensure_test_user(session, tu, dry_run)
        marker = {"created": "+", "existing": "·", "marked": "±",
                  "would-create": "?"}[action]
        label = tu.get("key") or str(tu["telegram_id"])

        if dry_run or user is None:
            # План без записи. В dry-run Practice-объектов нет — берём число
            # практик из JSON (src_*), иначе из реальных списков.
            avail_completed = len(completed) or src_completed
            avail_scheduled = len(scheduled) or src_scheduled
            n_att = min(cfg["attended_bookings"], avail_completed)
            n_up = min(cfg["upcoming_bookings"], avail_scheduled)
            n_can = min(cfg["cancelled_bookings"],
                        max(0, avail_scheduled - n_up))
            print(f"  {marker} {label:<14s} TID {tu['telegram_id']}  → "
                  f"дневник≈{min(cfg['diary_entries'], len(pools['diary']))}, "
                  f"attended≈{n_att}, чек-ины≈{min(cfg['checkins'], n_att)}, "
                  f"отзывы≈{min(cfg['feedbacks'], n_att)}, "
                  f"будущие≈{n_up}, отменённые≈{n_can}, "
                  f"граничные≈{src_boundary}")
            continue

        stats = await seed_one_test_user(
            session, user, cfg, completed, scheduled, batch_iso, pools,
            boundary,
        )
        print(f"  {marker} {label:<14s} TID {tu['telegram_id']}  → "
              f"дневник={stats['diary']}, attended={stats['attended']}, "
              f"чек-ины={stats['checkins']}, отзывы={stats['feedbacks']}, "
              f"будущие={stats['upcoming']}, отменённые={stats['cancelled']}, "
              f"граничные={stats['boundary']}")


# ─────────────────────────────────────────────────────────────────────────────
# CLEAN (FK-safe порядок DELETE, по образцу tests/helpers.py:full_cleanup_range)
# ─────────────────────────────────────────────────────────────────────────────

async def _collect_our_ids(
    session: AsyncSession,
) -> tuple[list, list, list, list]:
    """Один раз в начале clean захватываем все нужные ID в Python-списки.

    Критично: после DELETE MasterProfile подзапрос по JSONB-маркеру
    перестанет находить наших юзеров, и шаг "DELETE users" станет no-op.
    Поэтому сначала SELECT всё нужное в память, потом DELETE по спискам.

    Возвращает (master_ids, practice_ids, purchase_ids, withdrawal_ids).
    """
    master_ids_q = await session.execute(
        select(User.id)
        .join(MasterProfile, MasterProfile.user_id == User.id)
        .where(MasterProfile.data["seed"]["source"].astext == SEED_SOURCE),
    )
    master_ids = [row[0] for row in master_ids_q.all()]

    # Практики собираем по МАРКЕРУ seed.source — это ловит и практики служебных
    # мастеров, и практики тестеров-мастеров (master_id = реальный тестер, его
    # MasterProfile помечен SEED_SOURCE_TESTER и в master_ids НЕ попадает).
    practice_ids_q = await session.execute(
        select(Practice.id).where(
            Practice.data["seed"]["source"].astext == SEED_SOURCE,
        ),
    )
    practice_ids = [row[0] for row in practice_ids_q.all()]

    if not master_ids and not practice_ids:
        return [], [], [], []

    purchase_ids: list = []
    withdrawal_ids: list = []
    if master_ids:
        purchase_ids = [row[0] for row in (await session.execute(
            select(Purchase.id).where(Purchase.user_id.in_(master_ids)),
        )).all()]
        withdrawal_ids = [row[0] for row in (await session.execute(
            select(Withdrawal.id).where(Withdrawal.user_id.in_(master_ids)),
        )).all()]

    return master_ids, practice_ids, purchase_ids, withdrawal_ids


    return master_ids, practice_ids, purchase_ids, withdrawal_ids


async def _collect_test_user_ids(session: AsyncSession) -> list:
    """ID тест-юзеров по маркеру credentials.seed.source. Это первичный способ
    их найти (JSON со списком может быть не передан в clean-режиме).

    ВКЛЮЧАЕТ синтетических участников (у них тот же source). Вызывающий код
    отделяет их через _collect_synthetic_ids: реальные тестеры сохраняются,
    синтетики удаляются целиком."""
    q = await session.execute(
        select(User.id).where(
            User.credentials["seed"]["source"].astext == SEED_SOURCE,
        ),
    )
    return [row[0] for row in q.all()]


async def _collect_synthetic_ids(session: AsyncSession) -> list:
    """ID синтетических участников (credentials.seed.synthetic == true) —
    фейк-аккаунты, удаляемые при clean целиком."""
    q = await session.execute(
        select(User.id).where(
            User.credentials["seed"]["synthetic"].astext == "true",
        ),
    )
    return [row[0] for row in q.all()]


async def _purge_synthetic_participants(
    session: AsyncSession, synthetic_ids: list,
) -> None:
    """Полностью удаляет синтетических участников: сперва RESTRICT-ссылки
    (purchases / *_ledger / payments по user_id), затем сами аккаунты — их
    bookings/checkins/feedbacks/diary_events уходят каскадом по user_id."""
    if not synthetic_ids:
        return
    synth_purchase_ids = [r[0] for r in (await session.execute(
        select(Purchase.id).where(Purchase.user_id.in_(synthetic_ids)),
    )).all()]
    if synth_purchase_ids:
        await session.execute(delete(CompanyLedger).where(
            CompanyLedger.reference_id.in_([str(p) for p in synth_purchase_ids]),
        ))
        await session.execute(delete(AuditLog).where(
            AuditLog.target_id.in_(synth_purchase_ids),
        ))
    await session.execute(delete(Purchase).where(
        Purchase.user_id.in_(synthetic_ids),
    ))
    await session.execute(delete(MasterLedger).where(
        MasterLedger.user_id.in_(synthetic_ids),
    ))
    await session.execute(delete(UserLedger).where(
        UserLedger.user_id.in_(synthetic_ids),
    ))
    await session.execute(delete(Payment).where(
        Payment.user_id.in_(synthetic_ids),
    ))
    await session.execute(delete(User).where(User.id.in_(synthetic_ids)))


async def _purge_tester_master_ledger(
    session: AsyncSession, tester_ids: list,
) -> None:
    """Удаляет seed-проводки master_ledger у тестеров-мастеров (sale-кредиты от
    броней синтетиков на их практики). Не-seed проводки (без префикса 'seed:')
    не трогаются; сами аккаунты тестеров сохраняются."""
    if not tester_ids:
        return
    await session.execute(delete(MasterLedger).where(
        MasterLedger.user_id.in_(tester_ids),
        MasterLedger.reason.like("seed:%"),
    ))


async def _collect_test_user_data_ids(
    session: AsyncSession, test_user_ids: list, practice_ids: list,
) -> dict:
    """Собираем в память ВСЕ ID пользовательских seed-данных ДО первого DELETE.

    Практико-привязанные сущности (bookings/checkins/feedbacks/purchases) берём
    строго пересечением user_id ∈ test_users AND practice_id ∈ наши практики —
    чтобы у реального аккаунта не задеть его данные на ЧУЖИХ практиках.
    Личные записи дневника — через маркер DiaryEvent.snapshot.seed (source_id).
    """
    out = {
        "booking_ids": [], "checkin_ids": [], "feedback_ids": [],
        "purchase_ids": [], "diary_entry_ids": [],
    }
    if test_user_ids and practice_ids:
        out["booking_ids"] = [r[0] for r in (await session.execute(
            select(Booking.id).where(
                Booking.user_id.in_(test_user_ids),
                Booking.practice_id.in_(practice_ids),
            ),
        )).all()]
        out["checkin_ids"] = [r[0] for r in (await session.execute(
            select(Checkin.id).where(
                Checkin.user_id.in_(test_user_ids),
                Checkin.practice_id.in_(practice_ids),
            ),
        )).all()]
        out["feedback_ids"] = [r[0] for r in (await session.execute(
            select(Feedback.id).where(
                Feedback.user_id.in_(test_user_ids),
                Feedback.practice_id.in_(practice_ids),
            ),
        )).all()]
        out["purchase_ids"] = [r[0] for r in (await session.execute(
            select(Purchase.id).where(
                Purchase.user_id.in_(test_user_ids),
                Purchase.practice_id.in_(practice_ids),
            ),
        )).all()]
    if test_user_ids:
        # Личные note/dream нашего сидера: ловим помеченные diary_entry-события,
        # их source_id == DiaryEntry.id.
        out["diary_entry_ids"] = [r[0] for r in (await session.execute(
            select(DiaryEvent.source_id).where(
                DiaryEvent.user_id.in_(test_user_ids),
                DiaryEvent.source_type == "diary_entry",
                DiaryEvent.snapshot["seed"]["source"].astext == SEED_SOURCE,
            ),
        )).all()]
    return out


async def _clean_test_user_data(
    session: AsyncSession,
    test_user_ids: list,
    practice_ids: list,
    ids: dict,
    *,
    unmark_users: bool = False,
) -> None:
    """FK-safe удаление ТОЛЬКО наших пользовательских seed-данных.
    Никогда не удаляет сам User и его не-seed данные."""
    src_obj_ids = ids["booking_ids"] + ids["checkin_ids"] + ids["feedback_ids"]

    # U1. diary_events: маркер ИЛИ привязка к нашим практикам/объектам.
    await session.execute(delete(DiaryEvent).where(
        DiaryEvent.user_id.in_(test_user_ids),
        or_(
            DiaryEvent.snapshot["seed"]["source"].astext == SEED_SOURCE,
            and_(
                DiaryEvent.source_type.in_(["booking", "checkin", "feedback"]),
                DiaryEvent.source_id.in_(src_obj_ids),
            ),
            and_(
                DiaryEvent.source_type == "practice",
                DiaryEvent.source_id.in_(practice_ids),
            ),
        ),
    ))

    # U2. diary_entries: личные note/dream (по собранным source_id).
    if ids["diary_entry_ids"]:
        await session.execute(delete(DiaryEntry).where(
            DiaryEntry.id.in_(ids["diary_entry_ids"]),
        ))

    # U3/U4. checkins / feedbacks (CASCADE FK — RESTRICT не выстрелит).
    if ids["checkin_ids"]:
        await session.execute(delete(Checkin).where(
            Checkin.id.in_(ids["checkin_ids"]),
        ))
    if ids["feedback_ids"]:
        await session.execute(delete(Feedback).where(
            Feedback.id.in_(ids["feedback_ids"]),
        ))

    # U5. audit_logs purchase_completed (target_id == наш purchase id).
    if ids["purchase_ids"]:
        await session.execute(delete(AuditLog).where(
            AuditLog.target_id.in_(ids["purchase_ids"]),
        ))

    # U6. company_ledger: reference_id text-UUID нашего purchase.
    if ids["purchase_ids"]:
        await session.execute(delete(CompanyLedger).where(
            CompanyLedger.reference_id.in_(
                [str(pid) for pid in ids["purchase_ids"]],
            ),
        ))

    # U7. user_ledger: zero-amount проводки create_seed_booking
    #     (reason="seed:purchase:practice={pid}"). Скоуп — наши практики + наши
    #     тест-юзеры, поэтому чужие seed-проводки не заденем.
    for pid in practice_ids:
        await session.execute(delete(UserLedger).where(
            UserLedger.user_id.in_(test_user_ids),
            UserLedger.reason.like(f"%practice={pid}%"),
        ))

    # U8. purchases: RESTRICT на practice/booking → удаляем ДО bookings/practices.
    if ids["purchase_ids"]:
        await session.execute(delete(Purchase).where(
            Purchase.id.in_(ids["purchase_ids"]),
        ))

    # U9. bookings.
    if ids["booking_ids"]:
        await session.execute(delete(Booking).where(
            Booking.id.in_(ids["booking_ids"]),
        ))

    # U10. (опц.) снять маркер credentials.seed — «забыть», что трогали аккаунт.
    if unmark_users:
        users = (await session.execute(
            select(User).where(User.id.in_(test_user_ids)),
        )).scalars().all()
        for u in users:
            creds = dict(u.credentials or {})
            if "seed" in creds:
                creds.pop("seed", None)
                u.set_jsonb("credentials", creds)


async def cmd_clean(session: AsyncSession, dry_run: bool) -> None:
    prefix = "[DRY-RUN] " if dry_run else ""
    print(f"\n=== CLEAN ===")
    print(f"{prefix}Удаление наших seed-данных (мастера+практики с маркером "
          f"data.seed.source=='{SEED_SOURCE}' и пользовательские данные "
          f"тест-юзеров с маркером credentials.seed). Реальные аккаунты и их "
          f"не-seed данные не трогаются.")

    master_ids, practice_ids, purchase_ids, withdrawal_ids = \
        await _collect_our_ids(session)
    test_user_ids = await _collect_test_user_ids(session)

    # Синтетических участников отделяем: реальные тестеры сохраняются, синтетики
    # удаляются целиком (ЭТАП C).
    synthetic_ids = await _collect_synthetic_ids(session)
    synthetic_set = set(synthetic_ids)
    real_test_user_ids = [i for i in test_user_ids if i not in synthetic_set]

    if not master_ids and not test_user_ids and not practice_ids:
        print("  Нет данных для удаления.")
        return

    # Пользовательские sub-ID собираем ДО любого DELETE (только реальные тестеры;
    # данные синтетиков снесёт ЭТАП C каскадом по аккаунту).
    tu_ids = await _collect_test_user_data_ids(
        session, real_test_user_ids, practice_ids,
    )

    # Строковые версии UUID для company_ledger.reference_id и Notification JSONB
    master_ids_str = [str(uid) for uid in master_ids]
    practice_ids_str = [str(pid) for pid in practice_ids]
    purchase_ids_str = [str(pid) for pid in purchase_ids]
    withdrawal_ids_str = [str(wid) for wid in withdrawal_ids]

    if dry_run:
        # Считаем, что бы удалили
        if practice_ids:
            bookings_on_ours = (await session.execute(
                select(Booking).where(Booking.practice_id.in_(practice_ids)),
            )).scalars().all()
            purchases_on_ours = (await session.execute(
                select(Purchase).where(Purchase.practice_id.in_(practice_ids)),
            )).scalars().all()
        else:
            bookings_on_ours = []
            purchases_on_ours = []

        print(f"  Мастеров:  {len(master_ids)}")
        print(f"  Практик:   {len(practice_ids)}")
        print(f"  Bookings на наши практики (любых юзеров):  {len(bookings_on_ours)}")
        print(f"  Purchases на наши практики (любых юзеров): {len(purchases_on_ours)}")
        print(f"  Purchases у наших мастеров (нетипично):    {len(purchase_ids)}")
        print(f"  Withdrawals у наших мастеров:              {len(withdrawal_ids)}")
        print(f"  ── Тест-юзеры (реальные, сохраняются): {len(real_test_user_ids)}")
        print(f"  ── Синтетики (удаляются целиком):       {len(synthetic_ids)}")
        print(f"     Их bookings на наши практики:   {len(tu_ids['booking_ids'])}")
        print(f"     Их checkins на наши практики:   {len(tu_ids['checkin_ids'])}")
        print(f"     Их feedbacks на наши практики:  {len(tu_ids['feedback_ids'])}")
        print(f"     Их purchases на наши практики:  {len(tu_ids['purchase_ids'])}")
        print(f"     Их личных записей дневника:     {len(tu_ids['diary_entry_ids'])}")
        # purchases от ЧУЖИХ (не наших мастеров и не наших тест-юзеров)
        foreign_purchases = (
            len(purchases_on_ours) - len(tu_ids["purchase_ids"])
        )
        if foreign_purchases > 0:
            print()
            print(f"  !! ВНИМАНИЕ: на наших практиках есть ~{foreign_purchases} "
                  f"purchase(s) НЕ от наших тест-юзеров.")
            print("     RESTRICT FK на purchases.practice_id не даст удалить")
            print("     практики, пока эти purchases существуют. На пустом")
            print("     стенде такого быть не должно — разбирайся вручную.")
        print("\n[DRY-RUN] Изменения в БД НЕ зафиксированы.")
        return

    # ── Реальное удаление ─────────────────────────────────────────────────────

    # ЭТАП A: пользовательские данные РЕАЛЬНЫХ тест-юзеров (ДО удаления практик,
    # т.к. их purchases имеют RESTRICT на practice_id). Аккаунты сохраняются.
    if real_test_user_ids:
        await _clean_test_user_data(
            session, real_test_user_ids, practice_ids, tu_ids,
            unmark_users=False,
        )

    # ЭТАП B: данные служебных мастеров (FK-safe порядок, как было).
    if master_ids:
        # 1. notification_deliveries: FK -> notifications.id (CASCADE), users.id (CASCADE)
        await session.execute(delete(NotificationDelivery).where(
            NotificationDelivery.user_id.in_(master_ids),
        ))

        # 2. notifications: нет FK на users, фильтр по target_value (str-UUID) и
        #    action_data->>'practice_id'.
        if master_ids_str or practice_ids_str:
            await session.execute(delete(Notification).where(
                or_(
                    Notification.target_value.in_(master_ids_str),
                    Notification.action_data["practice_id"].astext.in_(practice_ids_str),
                ),
            ))

        # 3. checkins: FK -> users.id (CASCADE), practices.id (SET NULL)
        # 4. feedbacks: то же
        await session.execute(delete(Checkin).where(
            Checkin.user_id.in_(master_ids),
        ))
        await session.execute(delete(Feedback).where(
            Feedback.user_id.in_(master_ids),
        ))

        # 5. audit_logs: actor_id наш
        await session.execute(delete(AuditLog).where(
            AuditLog.actor_id.in_(master_ids),
        ))

        # 6. company_ledger: нет FK, reference_id text-UUID
        if purchase_ids_str or practice_ids_str or withdrawal_ids_str:
            all_ref_ids = purchase_ids_str + practice_ids_str + withdrawal_ids_str
            await session.execute(delete(CompanyLedger).where(
                CompanyLedger.reference_id.in_(all_ref_ids),
            ))

        # 7. master_ledger: user_id (RESTRICT), practices.id (SET NULL)
        #    Покрывает и проводки-кредиты нашим мастерам от броней тест-юзеров.
        # 8. user_ledger: user_id (RESTRICT)
        # 9. payments: user_id (RESTRICT)
        await session.execute(delete(MasterLedger).where(
            MasterLedger.user_id.in_(master_ids),
        ))
        await session.execute(delete(UserLedger).where(
            UserLedger.user_id.in_(master_ids),
        ))
        await session.execute(delete(Payment).where(
            Payment.user_id.in_(master_ids),
        ))

        # 10. purchases: user_id (RESTRICT), bookings.id (RESTRICT),
        #     practices.id (RESTRICT). Должно предшествовать bookings/practices.
        await session.execute(delete(Purchase).where(
            Purchase.user_id.in_(master_ids),
        ))

        # 11. waitlist / bookings / withdrawals / reports
        await session.execute(delete(Waitlist).where(
            Waitlist.user_id.in_(master_ids),
        ))
        await session.execute(delete(Booking).where(
            Booking.user_id.in_(master_ids),
        ))
        await session.execute(delete(Withdrawal).where(
            Withdrawal.user_id.in_(master_ids),
        ))
        await session.execute(delete(Report).where(
            Report.reporter_id.in_(master_ids),
        ))

        # 12. promos: master_id (CASCADE), practices.id (SET NULL)
        await session.execute(delete(Promo).where(
            Promo.master_id.in_(master_ids),
        ))

        # 12b. FK safety-net: снести ЛЮБЫЕ оставшиеся строки, ссылающиеся на наши
        #      seed-практики, до удаления самих практик (purchases/bookings имеют
        #      RESTRICT на practice_id). Покрывает «чужие» purchases/bookings — напр.
        #      реальный аккаунт, который через приложение записался на seed-практику
        #      и создал purchase: seed-скоупные шаги выше их не ловят (нет маркера
        #      credentials.seed / не наш мастер). Строго по practice_ids (наши seed-
        #      практики), поэтому НЕ-seed практики и их данные не трогаются. Без
        #      этого --reset падал на FK и требовал полного wipe БД. Порядок: audit/
        #      ledger по purchase -> purchases -> waitlist -> bookings (как в шагах 10-11).
        if practice_ids:
            leftover_purchase_ids = [r[0] for r in (await session.execute(
                select(Purchase.id).where(Purchase.practice_id.in_(practice_ids)),
            )).all()]
            if leftover_purchase_ids:
                lp_str = [str(p) for p in leftover_purchase_ids]
                await session.execute(delete(AuditLog).where(
                    AuditLog.target_id.in_(leftover_purchase_ids),
                ))
                await session.execute(delete(CompanyLedger).where(
                    CompanyLedger.reference_id.in_(lp_str),
                ))
                await session.execute(delete(Purchase).where(
                    Purchase.id.in_(leftover_purchase_ids),
                ))
            await session.execute(delete(Waitlist).where(
                Waitlist.practice_id.in_(practice_ids),
            ))
            await session.execute(delete(Booking).where(
                Booking.practice_id.in_(practice_ids),
            ))

        # 13. practices (наши) — к этому моменту ни test-user, ни master, ни
        #     «чужие» purchases/bookings их уже не держат.
        if practice_ids:
            await session.execute(delete(Practice).where(
                Practice.id.in_(practice_ids),
            ))

        # 14. master_profiles
        await session.execute(delete(MasterProfile).where(
            MasterProfile.user_id.in_(master_ids),
        ))

        # 15. users (наши служебные — по списку, не по подзапросу)
        await session.execute(delete(User).where(
            User.id.in_(master_ids),
        ))

    # ЭТАП C: мастер-сторона тестеров. Их практики уже удалены (ЭТАП B по
    # маркеру), брони/purchases синтетиков на них — тоже (FK safety-net). Здесь:
    # seed-проводки master_ledger тестеров (sale-кредиты) + полное удаление
    # синтетических участников (ledger по user_id, затем аккаунт → каскад).
    await _purge_tester_master_ledger(session, real_test_user_ids)
    await _purge_synthetic_participants(session, synthetic_ids)

    await session.commit()
    print(f"Clean завершён: мастеров {len(master_ids)}, практик "
          f"{len(practice_ids)}; синтетиков удалено {len(synthetic_ids)}; "
          f"реальных тест-юзеров затронуто {len(real_test_user_ids)} "
          f"(bookings {len(tu_ids['booking_ids'])}, checkins "
          f"{len(tu_ids['checkin_ids'])}, feedbacks {len(tu_ids['feedback_ids'])}, "
          f"личных записей {len(tu_ids['diary_entry_ids'])}). "
          f"Сами аккаунты тест-юзеров НЕ удалялись.")


# ─────────────────────────────────────────────────────────────────────────────
# promote-master — выдать ОДНОМУ реальному юзеру роль master + verified-профиль
# ─────────────────────────────────────────────────────────────────────────────
#
# Зачем отдельно от seed: штатный seed-путь сеет практики/мастеров из schedule и
# НЕ делает персистентного master (тестеры держатся на role=user + роль-свитч,
# который на проде выключен). Эта команда хирургическая: трогает РОВНО одного
# юзера (по telegram_id), синхронно ставит User.role=master И verified
# MasterProfile (инвариант консистентности 1.3 остаётся зелёным), ничего больше
# не добавляет и не сносит.
#
# Маркер профиля — отдельный MANUAL_GRANT_SOURCE (НЕ SEED_SOURCE), поэтому
# clean/reset НИКОГДА не заденут этот живой аккаунт.
#
# Идемпотентна и ПЕРЕЗАПИСЫВАЕМА: повторный запуск с обновлённым JSON
# перезаписывает profile.display_name/methods/bio (account/verification/payout/
# stats/баланс сохраняются). Сценарий — seed_scenarios/<name>.json с секцией
# promote_master. НЕ требует schedule/extends (мимо resolve_source).

def load_promote_scenario(scenario: str, explicit_source: str | None) -> dict:
    """Читает JSON-сценарий и возвращает блок promote_master.

    Путь: --source PATH (приоритет) либо seed_scenarios/<scenario>.json.
    """
    path = (
        Path(explicit_source)
        if explicit_source
        else SCENARIOS_DIR / f"{scenario}.json"
    )
    if not path.exists():
        raise FileNotFoundError(f"Сценарий не найден: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg = data.get("promote_master")
    if not isinstance(cfg, dict):
        raise ValueError(f"{path.name}: нет секции 'promote_master'")
    if not cfg.get("telegram_id"):
        raise ValueError(f"{path.name}: promote_master.telegram_id обязателен")
    return cfg


def _build_manual_master_data(
    user: User,
    display_name: str | None,
    methods: list[str],
    bio: str | None,
    existing: dict | None,
) -> dict:
    """MasterProfile.data для ручной выдачи мастера (всегда verified).

    Мержим поверх существующего data (re-run сохраняет payout/stats/verification),
    перезаписывая публичные поля профиля из JSON. display_name пуст -> фолбэк на
    User.first_name (как в get_master_display_name).
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    data = copy.deepcopy(existing) if existing else {}

    acct = data.setdefault("account", {})
    acct["status"] = "verified"
    acct.setdefault("applied_at", now_iso)
    acct.setdefault(
        "verification",
        {
            "verified_at": now_iso,
            "verified_by": "manual_grant",
            "notes": "manual master grant via seed_practices promote-master",
        },
    )
    acct.setdefault("rejections", [])

    prof = data.setdefault("profile", {})
    prof["display_name"] = display_name or prof.get("display_name") or user.first_name
    if methods:
        prof["methods"] = methods
    else:
        prof.setdefault("methods", [])
    if bio is not None:
        prof["bio"] = bio
    else:
        prof.setdefault("bio", None)
    prof.setdefault("email", None)
    prof.setdefault("phone", None)
    prof.setdefault("experience_years", None)
    prof.setdefault("certifications", [])

    data.setdefault("documents", [])
    data.setdefault("availability", {"is_accepting": True, "note": None})
    data.setdefault(
        "settings",
        {"auto_confirm_bookings": True, "max_participants_default": 20},
    )
    data.setdefault(
        "stats",
        {"total_practices": 0, "total_participants": 0, "avg_rating": None},
    )
    data["seed"] = {
        "source": MANUAL_GRANT_SOURCE,
        "telegram_id": user.telegram_id,
        "granted_at": now_iso,
    }
    return data


async def cmd_promote_master(
    session: AsyncSession, cfg: dict, dry_run: bool,
) -> None:
    tid = int(cfg["telegram_id"])
    display_name = cfg.get("display_name")
    methods = list(cfg.get("methods") or [])
    bio = cfg.get("bio")
    prefix = "[DRY-RUN] " if dry_run else ""

    print("\n=== PROMOTE-MASTER ===")
    print(f"{prefix}telegram_id: {tid}")

    user = await _find_user_by_tid(session, tid)
    if user is None:
        raise RuntimeError(
            f"Юзер с telegram_id={tid} не найден в БД. Этот аккаунт должен хоть "
            f"раз открыть бота (создать строку User), затем повтори команду."
        )

    existing_profile = await session.get(MasterProfile, user.id)
    new_data = _build_manual_master_data(
        user,
        display_name,
        methods,
        bio,
        existing_profile.data if existing_profile else None,
    )
    resolved_name = new_data["profile"]["display_name"]
    resolved_methods = new_data["profile"]["methods"]
    # user.role is a plain str on load (column is String(20), not an Enum type),
    # so format it directly — `.value` would AttributeError. The == below still
    # works: UserRole is a StrEnum, equal to its string value.
    role_note = (
        "уже master"
        if user.role == UserRole.MASTER
        else f"{user.role} -> master"
    )
    prof_note = "обновим" if existing_profile else "создадим"

    print(f"  user.id={user.id}  role: {role_note}")
    print(
        f"  профиль ({prof_note}, verified): "
        f"display_name={resolved_name!r}, methods={resolved_methods}"
    )

    if dry_run:
        print(f"\n{prefix}Ничего не записано.")
        return

    if existing_profile:
        existing_profile.set_jsonb("data", new_data)
    else:
        profile = MasterProfile(user_id=user.id)
        profile.set_jsonb("data", new_data)
        session.add(profile)
    user.role = UserRole.MASTER

    await session.flush()
    await session.commit()
    print("\nГотово, изменения зафиксированы (role=master + verified-профиль).")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> int:
    args = parse_args()

    # Деструктивные операции требуют подтверждения (если не --yes и не --dry-run).
    if args.command in ("reset", "clean") and not args.yes and not args.dry_run:
        if not confirm_destructive(args.command):
            print("Отменено.")
            return 1

    # promote-master не деструктивна, но меняет роль реального аккаунта —
    # лёгкое подтверждение (если не --yes/--dry-run).
    if args.command == "promote-master" and not args.yes and not args.dry_run:
        print()
        print(
            f"!! PROMOTE-MASTER: выдать роль master по сценарию "
            f"'{args.source or args.scenario}'."
        )
        if input('   Введите "yes" для подтверждения: ').strip().lower() != "yes":
            print("Отменено.")
            return 1

    source = (
        load_source(args.scenario, args.source)
        if args.command in ("seed", "reset") else None
    )
    session_factory = get_session_factory()

    try:
        if args.command == "seed":
            async with session_factory() as session:
                await cmd_seed(session, source, args.dry_run)
        elif args.command == "promote-master":
            cfg = load_promote_scenario(args.scenario, args.source)
            async with session_factory() as session:
                await cmd_promote_master(session, cfg, args.dry_run)
        elif args.command == "clean":
            async with session_factory() as session:
                await cmd_clean(session, args.dry_run)
        elif args.command == "reset":
            # Reset = clean + seed. Каждый этап в своей сессии (clean коммитит
            # своё, потом seed открывает новую сессию и коммитит своё).
            async with session_factory() as session:
                await cmd_clean(session, args.dry_run)
            async with session_factory() as session:
                await cmd_seed(session, source, args.dry_run)
    finally:
        await dispose_engine()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
