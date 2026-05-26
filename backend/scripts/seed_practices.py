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
  --dry-run            -- флаг к любому режиму. Показывает план без записи в БД.
  --yes                -- пропустить интерактивное подтверждение (для скриптинга).

Запуск:
  docker compose exec app python scripts/seed_practices.py
  docker compose exec app python scripts/seed_practices.py --reset
  docker compose exec app python scripts/seed_practices.py --clean
  docker compose exec app python scripts/seed_practices.py --reset --dry-run
  docker compose exec app python scripts/seed_practices.py --reset --yes

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
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── sys.path bootstrap ───────────────────────────────────────────────────────
# Кладём backend/scripts (для импорта соседнего seed.py) и backend (для app.*)
# в sys.path. backend/scripts — не пакет (нет __init__.py), поэтому seed.py
# импортируется как top-level модуль по имени файла. resolve() устойчив к ../.
_HERE = Path(__file__).resolve().parent          # backend/scripts
_BACKEND = _HERE.parent                           # backend
for _p in (_HERE, _BACKEND):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import dispose_engine, get_session_factory
from app.modules.audit.models import AuditLog
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
TID_MAX = 10011
JSON_PATH = Path(__file__).parent / "seed_practices.json"

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
# Подобраны так, чтобы лента была ~40 карточек и её было что листать:
#   12 личных записей + 7 attended (×2 карточки) + 6 чек-инов + 6 отзывов
#   + 1 будущая + 1 отменённая (×2) ≈ 41 элемент фида.
TEST_USER_DEFAULTS = {
    "diary_entries": 12,
    "attended_bookings": 7,
    "checkins": 6,
    "feedbacks": 6,
    "upcoming_bookings": 1,
    "cancelled_bookings": 1,
}

MOODS = ("low", "mid", "high")          # CHECK на Checkin.mood и DiaryEntry.mood
RATINGS = ("fire", "good", "confused")  # CHECK на Feedback.rating

# Личные записи дневника (note/dream). Backdate раскидан по ~20 дням назад.
# key — стабильный идентификатор шаблона (идёт в snapshot.seed.key); title
# уникален в рамках юзера (используется для идемпотентности).
SEED_V2_DIARY_TEMPLATES: list[dict] = [
    {"key": "note-01", "entry_type": "note", "practice_phase": "before",
     "mood": "mid", "offset_days": 1,
     "title": "Перед практикой — мысли роятся",
     "content": "Проснулась с тяжёлой головой, в мыслях уже список дел. "
                "Хочу за эти 60 минут просто замедлиться и выдохнуть."},
    {"key": "note-02", "entry_type": "note", "practice_phase": "after",
     "mood": "high", "offset_days": 1,
     "title": "После практики — будто перезагрузился",
     "content": "Тело гудит приятно, ум тихий. Удивительно, как 40 минут "
                "дыхания меняют весь настрой на день."},
    {"key": "dream-01", "entry_type": "dream", "practice_phase": None,
     "mood": None, "offset_days": 2,
     "title": "Сон про дом у воды",
     "content": "Снился старый дом на берегу, вода подходила к самому порогу, "
                "но было спокойно, а не тревожно. Проснулся с ощущением тепла."},
    {"key": "note-03", "entry_type": "note", "practice_phase": "before",
     "mood": "low", "offset_days": 3,
     "title": "Сегодня тяжело начинать",
     "content": "Сил почти нет, но пришёл на практику через не хочу. "
                "Посмотрим, что будет к концу."},
    {"key": "note-04", "entry_type": "note", "practice_phase": "after",
     "mood": "mid", "offset_days": 3,
     "title": "Отпустило к середине",
     "content": "Первые минут десять не мог поймать ритм, потом дыхание само "
                "выровнялось. Ушёл спокойнее, чем пришёл."},
    {"key": "dream-02", "entry_type": "dream", "practice_phase": None,
     "mood": None, "offset_days": 5,
     "title": "Сон: лечу над городом",
     "content": "Летал низко над крышами, без страха высоты. Кто-то снизу "
                "махал рукой. Яркие краски, давно так не снилось."},
    {"key": "note-05", "entry_type": "note", "practice_phase": None,
     "mood": "high", "offset_days": 6,
     "title": "Поймал состояние",
     "content": "Сегодня впервые за неделю почувствовал ту самую тишину внутри. "
                "Ничего не делал специально — просто случилось."},
    {"key": "note-06", "entry_type": "note", "practice_phase": "before",
     "mood": "mid", "offset_days": 8,
     "title": "Намерение на утро",
     "content": "Хочу сегодня меньше думать и больше чувствовать тело. "
                "Ставлю это как намерение перед началом."},
    {"key": "note-07", "entry_type": "note", "practice_phase": "after",
     "mood": "high", "offset_days": 8,
     "title": "Тело сказало спасибо",
     "content": "После телесной практики плечи опустились, дыхание стало "
                "глубже. Заметил, сколько напряжения носил и не замечал."},
    {"key": "dream-03", "entry_type": "dream", "practice_phase": None,
     "mood": None, "offset_days": 11,
     "title": "Сон про дорогу в горах",
     "content": "Шёл по горной тропе, туман то накрывал, то расходился. "
                "Не было цели дойти — просто шёл и смотрел."},
    {"key": "note-08", "entry_type": "note", "practice_phase": None,
     "mood": "low", "offset_days": 13,
     "title": "День, когда ничего не хотелось",
     "content": "Записываю честно: апатия. Практика не «починила» настроение, "
                "но хотя бы дала паузу, в которой можно было это заметить."},
    {"key": "note-09", "entry_type": "note", "practice_phase": "after",
     "mood": "mid", "offset_days": 15,
     "title": "Маленький сдвиг",
     "content": "Не фейерверк, но стало чуть легче. Учусь замечать такие "
                "небольшие изменения и не обесценивать их."},
    {"key": "note-10", "entry_type": "note", "practice_phase": "before",
     "mood": "mid", "offset_days": 17,
     "title": "Возвращаюсь к регулярности",
     "content": "Несколько дней пропускал. Сегодня снова на коврике — и уже "
                "одно это ощущается как маленькая победа."},
    {"key": "dream-04", "entry_type": "dream", "practice_phase": None,
     "mood": None, "offset_days": 19,
     "title": "Сон с давним другом",
     "content": "Разговаривали с человеком, которого давно не видел. Сон "
                "оставил тёплое послевкусие и желание написать ему."},
    {"key": "note-11", "entry_type": "note", "practice_phase": "after",
     "mood": "high", "offset_days": 20,
     "title": "Три недели практики",
     "content": "Оглядываюсь назад: стал спокойнее реагировать на мелочи, "
                "лучше сплю. Кажется, это работает не за один раз, а накопительно."},
]


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
        choices=("seed", "reset", "clean"),
        help="seed (default) | reset | clean",
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


def load_source() -> dict:
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"Источник не найден: {JSON_PATH}")
    with JSON_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    for m in data["masters"]:
        m["bio"] = _join_lines(m.get("bio"))
    for p in data["practices"]:
        p["description"] = _join_lines(p.get("description"))
        # what_to_prepare / contraindications обычно строки, но на всякий случай:
        p["what_to_prepare"] = _join_lines(p.get("what_to_prepare"))
        p["contraindications"] = _join_lines(p.get("contraindications"))
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
    if style is not None and len(style) > settings.practice_style_max_length:
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
) -> tuple[Practice | None, str]:
    existing = await _find_practice_by_key(session, p_yaml["key"])
    if existing:
        return existing, "existing"

    if dry_run:
        return None, "would-create"

    scheduled_at_str = p_yaml["scheduled_at"]
    scheduled_at = datetime.fromisoformat(scheduled_at_str)
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
    is_future = scheduled_at > datetime.now(timezone.utc)

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
    print(f"Источник: {JSON_PATH}")
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
            if p.get("status") == "completed":
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
        await cmd_seed_test_users(
            session,
            test_users,
            completed_practices,
            scheduled_practices,
            batch_iso,
            dry_run,
            src_completed=src_completed,
            src_scheduled=src_scheduled,
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


async def ensure_test_user(
    session: AsyncSession, tu: dict, dry_run: bool,
) -> tuple[User | None, str]:
    """find-or-create тест-юзера по telegram_id.

    Если юзер уже есть — НЕ меняем роль и НЕ перетираем его данные; только
    добавляем ключ credentials.seed (маркер «наш тест-юзер»). Если нет —
    создаём с role=USER. Возвращает (user, action) где
    action ∈ {created, existing, marked, would-create}.
    """
    existing = await _find_user_by_tid(session, tu["telegram_id"])
    if existing:
        if dry_run:
            return existing, "existing"
        creds = dict(existing.credentials or {})
        if creds.get("seed", {}).get("source") != SEED_SOURCE:
            creds["seed"] = {
                "source": SEED_SOURCE,
                "test_user_key": tu.get("key"),
                "first_seeded_at": _now().isoformat(),
            }
            existing.set_jsonb("credentials", creds)
            await session.flush()
            return existing, "marked"
        return existing, "existing"

    if dry_run:
        return None, "would-create"

    user = User(
        telegram_id=tu["telegram_id"],
        first_name=tu.get("first_name") or f"Tester {tu['telegram_id']}",
        last_name=tu.get("last_name"),
        role=UserRole.USER,
        is_active=True,
    )
    user.set_jsonb("credentials", {
        "onboarding_completed": True,
        "seed": {
            "source": SEED_SOURCE,
            "test_user_key": tu.get("key"),
            "first_seeded_at": _now().isoformat(),
        },
    })
    if tu.get("language"):
        # language — опциональное поле; ставим только если модель его принимает.
        if hasattr(user, "language"):
            user.language = tu["language"]
    session.add(user)
    await session.flush()
    return user, "created"


async def create_v2_diary_entries(
    session: AsyncSession, user: User, count: int, batch_iso: str,
) -> int:
    """Сеет личные записи дневника (note/dream) тест-юзеру. Backdate через
    entry.created_at ДО проекции, маркер — в snapshot.seed связанного DiaryEvent.
    Идемпотентно по (user_id, title, entry_type)."""
    created = 0
    now = _now()
    for tmpl in SEED_V2_DIARY_TEMPLATES[:count]:
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
    master_name: str | None, batch_iso: str, idx: int,
) -> bool:
    """Исторический pre-чек-ин ORM-insert'ом + ручная проекция в фид.
    Идемпотентно по UniqueConstraint(booking_id, check_type='pre')."""
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
        mood=MOODS[idx % len(MOODS)],
        comment="Настраиваюсь на практику." if idx % 2 == 0 else None,
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
    master_name: str | None, batch_iso: str, idx: int,
) -> bool:
    """Исторический отзыв ORM-insert'ом + ручная проекция в фид.
    Идемпотентно по UniqueConstraint(practice_id, user_id)."""
    dup = (await session.execute(
        select(Feedback.id).where(
            Feedback.practice_id == practice.id,
            Feedback.user_id == user.id,
        ).limit(1),
    )).scalar_one_or_none()
    if dup is not None:
        return False

    now = _now()
    comments = [
        "Очень мягко и бережно, ровно то, что было нужно утром.",
        "Сначала было непросто включиться, но к концу отпустило.",
        "Спасибо, ушёл с ясной головой и спокойным телом.",
    ]
    fb = Feedback(
        practice_id=practice.id,
        user_id=user.id,
        booking_id=booking.id,
        rating=RATINGS[idx % len(RATINGS)],
        comment=comments[idx % len(comments)],
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
             "feedbacks": 0, "upcoming": 0, "cancelled": 0}
    touched_practice_ids: set = set()

    # 1. Исторические attended-брони (+ confirmed/outcome события) на completed.
    attended_bookings: list[tuple[Practice, Booking]] = []
    for practice in completed[:n_attended]:
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
                                   master_name, batch_iso, i):
                stats["checkins"] += 1
        if i < n_feedbacks:
            if await _seed_feedback(session, user, practice, booking,
                                    master_name, batch_iso, i):
                stats["feedbacks"] += 1

    # 3. Будущие confirmed-брони на scheduled-практики.
    for practice in scheduled[:n_upcoming]:
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

    # 5. Личные записи дневника.
    stats["diary"] = await create_v2_diary_entries(
        session, user, cfg["diary_entries"], batch_iso,
    )

    # 6. Пересчёт участников по затронутым практикам (COUNT-based, идемпотентно).
    for pid in touched_practice_ids:
        await recalculate_participants(pid, session)

    return stats


async def cmd_seed_test_users(
    session: AsyncSession,
    test_users: list[dict],
    completed: list[Practice],
    scheduled: list[Practice],
    batch_iso: str,
    dry_run: bool,
    *,
    src_completed: int = 0,
    src_scheduled: int = 0,
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
                  f"дневник≈{min(cfg['diary_entries'], len(SEED_V2_DIARY_TEMPLATES))}, "
                  f"attended≈{n_att}, чек-ины≈{min(cfg['checkins'], n_att)}, "
                  f"отзывы≈{min(cfg['feedbacks'], n_att)}, "
                  f"будущие≈{n_up}, отменённые≈{n_can}")
            continue

        stats = await seed_one_test_user(
            session, user, cfg, completed, scheduled, batch_iso,
        )
        print(f"  {marker} {label:<14s} TID {tu['telegram_id']}  → "
              f"дневник={stats['diary']}, attended={stats['attended']}, "
              f"чек-ины={stats['checkins']}, отзывы={stats['feedbacks']}, "
              f"будущие={stats['upcoming']}, отменённые={stats['cancelled']}")


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

    if not master_ids:
        return [], [], [], []

    practice_ids_q = await session.execute(
        select(Practice.id).where(Practice.master_id.in_(master_ids)),
    )
    practice_ids = [row[0] for row in practice_ids_q.all()]

    purchase_ids_q = await session.execute(
        select(Purchase.id).where(Purchase.user_id.in_(master_ids)),
    )
    purchase_ids = [row[0] for row in purchase_ids_q.all()]

    withdrawal_ids_q = await session.execute(
        select(Withdrawal.id).where(Withdrawal.user_id.in_(master_ids)),
    )
    withdrawal_ids = [row[0] for row in withdrawal_ids_q.all()]

    return master_ids, practice_ids, purchase_ids, withdrawal_ids


    return master_ids, practice_ids, purchase_ids, withdrawal_ids


async def _collect_test_user_ids(session: AsyncSession) -> list:
    """ID тест-юзеров по маркеру credentials.seed.source. Это первичный способ
    их найти (JSON со списком может быть не передан в clean-режиме)."""
    q = await session.execute(
        select(User.id).where(
            User.credentials["seed"]["source"].astext == SEED_SOURCE,
        ),
    )
    return [row[0] for row in q.all()]


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

    if not master_ids and not test_user_ids:
        print("  Нет данных для удаления.")
        return

    # Пользовательские sub-ID собираем ДО любого DELETE.
    tu_ids = await _collect_test_user_data_ids(
        session, test_user_ids, practice_ids,
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
        print(f"  ── Тест-юзеры (по маркеру credentials.seed): {len(test_user_ids)}")
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

    # ЭТАП A: пользовательские данные тест-юзеров (ДО удаления практик, т.к.
    # их purchases имеют RESTRICT на practice_id).
    if test_user_ids:
        await _clean_test_user_data(
            session, test_user_ids, practice_ids, tu_ids, unmark_users=False,
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

        # 13. practices (наши) — к этому моменту ни test-user, ни master purchases
        #     их уже не держат.
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

    await session.commit()
    print(f"Clean завершён: мастеров {len(master_ids)}, практик "
          f"{len(practice_ids)}; тест-юзеров затронуто {len(test_user_ids)} "
          f"(bookings {len(tu_ids['booking_ids'])}, checkins "
          f"{len(tu_ids['checkin_ids'])}, feedbacks {len(tu_ids['feedback_ids'])}, "
          f"личных записей {len(tu_ids['diary_entry_ids'])}). "
          f"Сами аккаунты тест-юзеров НЕ удалялись.")


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

    source = load_source() if args.command in ("seed", "reset") else None
    session_factory = get_session_factory()

    try:
        if args.command == "seed":
            async with session_factory() as session:
                await cmd_seed(session, source, args.dry_run)
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
