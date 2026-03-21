#!/usr/bin/env python3
# =============================================================================
# VELO Backend -- Database Seed Script
# =============================================================================
#
# Populates the database with realistic test data for frontend development.
#
# USAGE (via management command):
#   velo seed            -- interactive seed (asks for Telegram IDs)
#   velo seed --reset    -- clean all seed data, then re-seed
#
# DIRECT USAGE (inside Docker container):
#   python scripts/seed.py
#   python scripts/seed.py --reset
#
# CREATED DATA:
#   - Up to 5 admins  (ADMIN role + verified MasterProfile)
#   - Up to 5 masters (MASTER role + verified MasterProfile)
#   - Up to 5 users   (USER role)
#   - 2 dummy masters + 28 dummy users (fixed, always created)
#   - 12 practices across all types and statuses
#   - Bookings with full double-entry ledger
#   - User balances via topup ledger entries
#
# ROLE RULES:
#   - Admin is always also a master (MasterProfile created).
#   - Same ID in multiple lists → highest role wins (ADMIN > MASTER > USER).
#   - Existing user with higher role than requested → warn, keep existing role.
#
# IDEMPOTENCY:
#   Repeated runs skip existing records (no duplicates).
#   --reset clears all seed data before re-creating.
#
# IDENTIFICATION (for cleanup):
#   - Seed practices: description ends with __SEED__ marker
#   - Seed ledger entries: reason starts with "seed:"
#   - Dummy users: telegram_id in range 9900001..9900030
# =============================================================================

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

# -- Ensure app package is importable when running as standalone script. --
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from sqlalchemy import case, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditLog, record_audit
from app.core.config import settings
from app.core.database import dispose_engine, get_session_factory
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.bookings.service import recalculate_participants
from app.modules.masters.models import MasterProfile
from app.modules.payments.models import (
    CompanyLedger,
    CompanyLedgerType,
    LedgerStatus,
    MasterLedger,
    Purchase,
    PurchaseStatus,
    UserLedger,
)
from app.modules.payments.service import (
    record_company_ledger,
    record_master_ledger,
    record_user_ledger,
)
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.users.models import User, UserRole


# ===================================================================
# Constants
# ===================================================================

DUMMY_TID_MIN = 9900001
DUMMY_TID_MAX = 9900030
SEED_MARKER = "\n__SEED__"
SEED_REASON = "seed:"

NOW = datetime.now(timezone.utc)
PRACTICE_TZ = "Europe/Berlin"

# Topup amounts in EUR cents.
# DUMMY_USER_TOPUP must exceed max possible practice debit sum across all
# templates a single dummy user might be booked into:
#   500+1000+2500+800+1200+1000+2000+1500+1800 = 12300 → 20000 is safe.
REAL_USER_TOPUP = 15000   # EUR 150.00
DUMMY_USER_TOPUP = 20000  # EUR 200.00 (covers worst-case booking debit sum)

# Terminal colors.
G = "\033[0;32m"
Y = "\033[1;33m"
R = "\033[0;31m"
C = "\033[0;36m"
B = "\033[1m"
N = "\033[0m"


def log(msg: str) -> None:
    print(f"{G}[SEED]{N} {msg}")


def warn(msg: str) -> None:
    print(f"{Y}[WARN]{N} {msg}")


def err(msg: str) -> None:
    print(f"{R}[ERROR]{N} {msg}")


# ===================================================================
# Dummy data
# ===================================================================

DUMMY_FIRST_NAMES: list[tuple[str, str | None]] = [
    ("Анна", "К."),
    ("Дмитрий", "С."),
    ("Елена", "М."),
    ("Алексей", "В."),
    ("Мария", "Б."),
    ("Иван", "Д."),
    ("Ольга", "П."),
    ("Сергей", "Л."),
    ("Наталья", "Ш."),
    ("Андрей", "Н."),
    ("Татьяна", "Р."),
    ("Павел", "Г."),
    ("Ксения", "Т."),
    ("Михаил", "Ж."),
    ("Юлия", "Ф."),
    ("Артём", "И."),
    ("Дарья", "О."),
    ("Максим", "Е."),
    ("Виктория", "А."),
    ("Никита", "Х."),
    ("Софья", "Ц."),
    ("Роман", "У."),
    ("Полина", "Я."),
    ("Егор", "З."),
    ("Валерия", "Ч."),
    ("Тимофей", "К."),
    ("Алиса", "В."),
    ("Кирилл", "М."),
]

DUMMY_MASTER_DATA = [
    {
        "tid": 9900029,
        "first_name": "Елена",
        "last_name": "Мирная",
        "display_name": "Елена Мирная",
        "bio": "Сертифицированный инструктор йоги (RYT-500). "
               "10 лет практики. Специализация: хатха, виньяса, инь.",
        "methods": ["hatha", "vinyasa", "yin"],
    },
    {
        "tid": 9900030,
        "first_name": "Олег",
        "last_name": "Спокойный",
        "display_name": "Олег Спокойный",
        "bio": "Мастер медитации и breathwork. Обучался в ашрамах "
               "Индии и Таиланда. Ведёт практики с 2018 года.",
        "methods": ["meditation", "breathwork", "sound_healing"],
    },
]


# ===================================================================
# Practice templates (12 practices)
# ===================================================================

PRACTICE_TEMPLATES: list[dict] = [
    # -- 0..5: Scheduled / Live (future or now) --
    {
        "title": "Утренняя медитация осознанности",
        "description": (
            "Начните день с ясности ума. Практика включает body scan, "
            "наблюдение за дыханием и работу с намерением на день."
        ),
        "what_to_prepare": "Удобная одежда, коврик или подушка для медитации.",
        "contraindications": None,
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.SCHEDULED.value,
        "duration_minutes": 30,
        "max_participants": 20,
        "is_free": False,
        "price_cents": 500,
        "offset": timedelta(days=3, hours=7),
        "num_bookings": 4,
    },
    {
        "title": "Виньяса флоу для начинающих",
        "description": (
            "Мягкая виньяса для тех, кто только начинает путь в йоге. "
            "Акцент на правильном дыхании и базовых асанах."
        ),
        "what_to_prepare": "Коврик для йоги, удобная одежда, вода.",
        "contraindications": "Травмы позвоночника, острые боли в суставах.",
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.SCHEDULED.value,
        "duration_minutes": 60,
        "max_participants": 15,
        "is_free": False,
        "price_cents": 1000,
        "offset": timedelta(days=5, hours=9),
        "num_bookings": 3,
    },
    {
        "title": "Breathwork: связное дыхание",
        "description": (
            "Индивидуальная сессия связного дыхания. "
            "Глубокая работа с телом и эмоциями."
        ),
        "what_to_prepare": "Удобная одежда, плед, коврик. Не есть за 2 часа до сессии.",
        "contraindications": "Беременность, эпилепсия, сердечно-сосудистые заболевания.",
        "practice_type": PracticeType.ONE_ON_ONE.value,
        "target_status": PracticeStatus.SCHEDULED.value,
        "duration_minutes": 45,
        "max_participants": 1,
        "is_free": False,
        "price_cents": 2500,
        "offset": timedelta(days=7, hours=15),
        "num_bookings": 1,
    },
    {
        "title": "Звуковая медитация с поющими чашами",
        "description": (
            "Погрузитесь в вибрации тибетских поющих чаш. "
            "Бесплатная практика для всех желающих."
        ),
        "what_to_prepare": "Коврик, плед, маска для глаз (по желанию).",
        "contraindications": None,
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.SCHEDULED.value,
        "duration_minutes": 90,
        "max_participants": 30,
        "is_free": True,
        "price_cents": 0,
        "offset": timedelta(days=10, hours=18),
        "num_bookings": 6,
    },
    {
        "title": "Йога-нидра: глубокое расслабление",
        "description": (
            "Техника осознанного расслабления, восстанавливающая "
            "нервную систему лучше нескольких часов обычного сна."
        ),
        "what_to_prepare": "Коврик, плед, подушка, маска для сна.",
        "contraindications": None,
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.SCHEDULED.value,
        "duration_minutes": 45,
        "max_participants": 25,
        "is_free": False,
        "price_cents": 800,
        "offset": timedelta(days=14, hours=20),
        "num_bookings": 3,
    },
    {
        "title": "Динамическая медитация",
        "description": (
            "Активная медитация с элементами движения и звука. "
            "Отпустите напряжение и войдите в состояние потока."
        ),
        "what_to_prepare": "Удобная одежда, в которой можно двигаться. Босиком или в носках.",
        "contraindications": "Острые травмы опорно-двигательного аппарата.",
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.LIVE.value,
        "duration_minutes": 60,
        "max_participants": 20,
        "is_free": False,
        "price_cents": 1200,
        "offset": timedelta(minutes=-30),
        "num_bookings": 7,
    },
    # -- 6..9: Completed (past) --
    {
        "title": "Утренняя хатха-йога",
        "description": (
            "Классическая хатха-йога: разминка, основные асаны, "
            "пранаяма и шавасана."
        ),
        "what_to_prepare": "Коврик для йоги, удобная одежда, вода.",
        "contraindications": "Беременность 2–3 триместр, острые боли в спине.",
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.COMPLETED.value,
        "duration_minutes": 60,
        "max_participants": 15,
        "is_free": False,
        "price_cents": 1000,
        "offset": timedelta(days=-7, hours=7),
        "num_bookings": 5,
    },
    {
        "title": "Медитация любящей доброты",
        "description": (
            "Метта-медитация: культивирование сострадания к себе "
            "и окружающим. Бесплатная групповая практика."
        ),
        "what_to_prepare": "Удобная одежда, коврик или стул.",
        "contraindications": None,
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.COMPLETED.value,
        "duration_minutes": 30,
        "max_participants": 50,
        "is_free": True,
        "price_cents": 0,
        "offset": timedelta(days=-14, hours=19),
        "num_bookings": 10,
    },
    {
        "title": "Пранаяма: техники дыхания",
        "description": (
            "Индивидуальная сессия: нади-шодхана, капалабхати, "
            "бхастрика. Подбор техник под ваши цели."
        ),
        "what_to_prepare": "Удобная одежда. Не есть за 1 час до занятия.",
        "contraindications": "Гипертония, эпилепсия, острые респираторные заболевания.",
        "practice_type": PracticeType.ONE_ON_ONE.value,
        "target_status": PracticeStatus.COMPLETED.value,
        "duration_minutes": 45,
        "max_participants": 1,
        "is_free": False,
        "price_cents": 2000,
        "offset": timedelta(days=-3, hours=14),
        "num_bookings": 1,
    },
    {
        "title": "Кундалини-йога: набхи-крия",
        "description": (
            "Крия для пупочного центра: укрепление core, работа "
            "с огненным дыханием, медитация Сат Нам."
        ),
        "what_to_prepare": "Белая одежда (традиция), коврик, покрывало.",
        "contraindications": "Беременность, высокое давление, эпилепсия.",
        "practice_type": PracticeType.SERIES.value,
        "target_status": PracticeStatus.COMPLETED.value,
        "duration_minutes": 75,
        "max_participants": 20,
        "is_free": False,
        "price_cents": 1500,
        "offset": timedelta(days=-21, hours=10),
        "num_bookings": 4,
    },
    # -- 10: Cancelled --
    {
        "title": "Танцевальная медитация 5 ритмов",
        "description": (
            "Практика отменена мастером. "
            "Следите за обновлениями в расписании."
        ),
        "what_to_prepare": None,
        "contraindications": None,
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.CANCELLED.value,
        "duration_minutes": 60,
        "max_participants": 20,
        "is_free": False,
        "price_cents": 1000,
        "offset": timedelta(days=2, hours=19),
        "num_bookings": 0,
    },
    # -- 11: Far future --
    {
        "title": "Ретрит: медитация при полной луне",
        "description": (
            "Особенная практика под открытым небом. Медитация, "
            "мантры и чайная церемония. Мест мало."
        ),
        "what_to_prepare": "Тёплая одежда, коврик, термос с чаем.",
        "contraindications": None,
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.SCHEDULED.value,
        "duration_minutes": 120,
        "max_participants": 40,
        "is_free": False,
        "price_cents": 1800,
        "offset": timedelta(days=30, hours=20),
        "num_bookings": 2,
    },
    # -- 12: BANNER -- check-in window (confirmed booking for all real users) --
    # scheduled_at = NOW + 90 min → inside CHECKIN_WINDOW_H=3h window.
    # Owner is always DUMMY_MASTER_DATA[0] (Елена Мирная, tid=9900029)
    # so no real user can be the practice master.
    {
        "title": "Утренняя медитация",
        "description": (
            "Мягкая медитация для начала дня. "
            "Дыхание, тело, намерение."
        ),
        "what_to_prepare": "Удобная одежда, коврик или подушка.",
        "contraindications": None,
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.SCHEDULED.value,
        "duration_minutes": 45,
        "max_participants": 100,
        "is_free": True,
        "price_cents": 0,
        "offset": timedelta(minutes=90),
        "num_bookings": 0,
        "seed_for_real_users": True,
        "fixed_master_tid": 9900029,
    },
    # -- 13: BANNER -- feedback window (attended booking for all real users) --
    # scheduled_at = NOW - 2h, duration=45min → ended 1h 15min ago,
    # well inside FEEDBACK_WINDOW_H=72h window.
    # Owner is always DUMMY_MASTER_DATA[1] (Олег Спокойный, tid=9900030).
    {
        "title": "Вечерняя медитация",
        "description": (
            "Практика завершения дня. "
            "Снятие напряжения и подготовка ко сну."
        ),
        "what_to_prepare": "Удобная одежда, плед, можно лечь на коврик.",
        "contraindications": None,
        "practice_type": PracticeType.LIVE.value,
        "target_status": PracticeStatus.COMPLETED.value,
        "duration_minutes": 45,
        "max_participants": 100,
        "is_free": True,
        "price_cents": 0,
        "offset": timedelta(hours=-2),
        "num_bookings": 0,
        "seed_for_real_users": True,
        "fixed_master_tid": 9900030,
    },
]


# ===================================================================
# Interactive input
# ===================================================================

def ask_telegram_ids() -> tuple[list[int], list[int], list[int]]:
    """Prompt for real Telegram IDs. Returns (master_tids, user_tids, admin_tids).

    Each list accepts up to 5 IDs; 0 is allowed for users and admins.
    At least one master or admin must be provided (so there is someone to
    own practices).

    Role priority when the same ID appears in multiple lists: ADMIN > MASTER > USER.
    The ID is assigned the highest role and a warning is printed.
    """
    print(f"\n{C}{'=' * 55}{N}")
    print(f"{C}  VELO Seed -- Enter real Telegram IDs{N}")
    print(f"{C}{'=' * 55}{N}")
    print(f"{Y}  Up to 5 IDs per role. Press Enter to skip / stop.{N}")
    print(f"{Y}  Admins are also masters (MasterProfile is created).{N}")
    print(f"{Y}  Same ID in multiple lists → highest role wins.{N}\n")

    def _read_ids(label: str, max_count: int, required: bool) -> list[int]:
        """Read up to max_count integer IDs interactively."""
        ids: list[int] = []
        for i in range(max_count):
            is_first = i == 0
            suffix = " (Enter to skip)" if not is_first or not required else ""
            while True:
                raw = input(f"  {label} {i + 1} Telegram ID{suffix}: ").strip()
                if not raw:
                    if is_first and required:
                        err("At least one ID is required.")
                        continue
                    return ids
                try:
                    ids.append(int(raw))
                    break
                except ValueError:
                    err("Must be a number.")
        return ids

    master_tids = _read_ids("Master", 5, required=True)
    print()
    user_tids = _read_ids("User", 5, required=False)
    print()
    admin_tids = _read_ids("Admin", 5, required=False)
    print()

    # Deduplicate within each list, preserving order.
    def _dedup(ids: list[int], label: str) -> list[int]:
        result = list(dict.fromkeys(ids))
        if len(result) < len(ids):
            warn(f"Duplicate {label} IDs removed — using unique only.")
        return result

    master_tids = _dedup(master_tids, "master")
    user_tids   = _dedup(user_tids,   "user")
    admin_tids  = _dedup(admin_tids,  "admin")

    # Resolve conflicts: ADMIN > MASTER > USER.
    # Build a mapping tid → highest role, then split back.
    _ROLE_RANK = {UserRole.USER: 0, UserRole.MASTER: 1, UserRole.ADMIN: 2}
    tid_role: dict[int, UserRole] = {}

    for tid in user_tids:
        tid_role[tid] = UserRole.USER
    for tid in master_tids:
        if tid not in tid_role or _ROLE_RANK[tid_role[tid]] < _ROLE_RANK[UserRole.MASTER]:
            tid_role[tid] = UserRole.MASTER
    for tid in admin_tids:
        if tid not in tid_role or _ROLE_RANK[tid_role[tid]] < _ROLE_RANK[UserRole.ADMIN]:
            tid_role[tid] = UserRole.ADMIN

    # Warn about any demotions.
    for tid in master_tids:
        if tid_role[tid] == UserRole.ADMIN:
            warn(f"TID {tid} appears in both master and admin lists — assigning ADMIN.")
    for tid in user_tids:
        if tid_role[tid] in (UserRole.MASTER, UserRole.ADMIN):
            warn(f"TID {tid} appears in user list but also in a higher role — assigning {tid_role[tid].value.upper()}.")

    # Rebuild clean lists from resolved mapping.
    master_tids = [t for t in master_tids if tid_role[t] == UserRole.MASTER]
    user_tids   = [t for t in user_tids   if tid_role[t] == UserRole.USER]
    admin_tids  = list(dict.fromkeys(
        [t for t in admin_tids] +
        [t for t, r in tid_role.items() if r == UserRole.ADMIN and t not in admin_tids]
    ))

    return master_tids, user_tids, admin_tids


# ===================================================================
# Reset (cleanup)
# ===================================================================

async def reset_seed_data(session: AsyncSession) -> None:
    """Delete all seed-created data in FK-safe order."""
    log("Resetting seed data...")

    # 1. Find seed practice IDs (by marker in description).
    stmt = select(Practice.id).where(
        Practice.description.like(f"%__SEED__%"),
    )
    seed_pids = [
        row[0] for row in (await session.execute(stmt)).all()
    ]

    # 2. Find dummy user IDs.
    stmt = select(User.id).where(
        User.telegram_id.between(DUMMY_TID_MIN, DUMMY_TID_MAX),
    )
    dummy_uids = [
        row[0] for row in (await session.execute(stmt)).all()
    ]

    # 3. Find real user IDs that have seed ledger entries
    #    (needed for balance recalculation after cleanup).
    stmt = (
        select(UserLedger.user_id.distinct())
        .where(UserLedger.reason.like(f"{SEED_REASON}%"))
    )
    affected_uids = [
        row[0] for row in (await session.execute(stmt)).all()
    ]

    # 4. Find real master IDs that have seed ledger entries.
    stmt = (
        select(MasterLedger.user_id.distinct())
        .where(MasterLedger.reason.like(f"{SEED_REASON}%"))
    )
    affected_mids = [
        row[0] for row in (await session.execute(stmt)).all()
    ]

    # -- Delete in FK order (RESTRICT-safe) --

    # 5. Company ledger.
    r = await session.execute(
        delete(CompanyLedger).where(
            CompanyLedger.reason.like(f"{SEED_REASON}%"),
        )
    )
    log(f"  CompanyLedger: {r.rowcount} deleted")

    # 6. Master ledger.
    r = await session.execute(
        delete(MasterLedger).where(
            MasterLedger.reason.like(f"{SEED_REASON}%"),
        )
    )
    log(f"  MasterLedger:  {r.rowcount} deleted")

    # 7. User ledger.
    r = await session.execute(
        delete(UserLedger).where(
            UserLedger.reason.like(f"{SEED_REASON}%"),
        )
    )
    log(f"  UserLedger:    {r.rowcount} deleted")

    # 8. Audit logs for seed purchases (must precede purchase deletion).
    if seed_pids:
        # Collect purchase IDs for seed practices before deleting them.
        purchase_ids_stmt = select(Purchase.id).where(
            Purchase.practice_id.in_(seed_pids)
        )
        seed_purchase_ids = [
            row[0] for row in (await session.execute(purchase_ids_stmt)).all()
        ]
        if seed_purchase_ids:
            r = await session.execute(
                delete(AuditLog).where(
                    AuditLog.target_id.in_(seed_purchase_ids),
                    AuditLog.event.in_({
                        "purchase_completed",
                        "purchase_refunded",
                    }),
                )
            )
            log(f"  AuditLog:      {r.rowcount} deleted")

    # 8b. UserLedger entries for seed practices (any reason containing practice id).
    # Covers both "seed:purchase:practice={pid}" and "purchase:practice={pid}"
    # (the latter occurs when real users buy seed practices through normal flow).
    if seed_pids:
        for pid in seed_pids:
            pid_str = str(pid)
            r = await session.execute(
                delete(UserLedger).where(
                    UserLedger.reason.like(f"%practice={pid_str}%"),
                )
            )
            if r.rowcount:
                log(f"  UserLedger (practice {pid_str[:8]}..): {r.rowcount} deleted")

    # 8c. MasterLedger entries for seed practices (by practice_id FK).
    if seed_pids:
        r = await session.execute(
            delete(MasterLedger).where(
                MasterLedger.practice_id.in_(seed_pids),
            )
        )
        log(f"  MasterLedger (by practice): {r.rowcount} deleted")

    # 9. Purchases for seed practices.
    if seed_pids:
        r = await session.execute(
            delete(Purchase).where(Purchase.practice_id.in_(seed_pids))
        )
        log(f"  Purchases:     {r.rowcount} deleted")

    # 10. Bookings for seed practices.
    if seed_pids:
        r = await session.execute(
            delete(Booking).where(Booking.practice_id.in_(seed_pids))
        )
        log(f"  Bookings:      {r.rowcount} deleted")

    # 11. Seed practices.
    if seed_pids:
        r = await session.execute(
            delete(Practice).where(Practice.id.in_(seed_pids))
        )
        log(f"  Practices:     {r.rowcount} deleted")

    # 12. Dummy master profiles.
    if dummy_uids:
        r = await session.execute(
            delete(MasterProfile).where(
                MasterProfile.user_id.in_(dummy_uids),
            )
        )
        log(f"  MasterProf:    {r.rowcount} deleted")

    # 13. Dummy users.
    r = await session.execute(
        delete(User).where(
            User.telegram_id.between(DUMMY_TID_MIN, DUMMY_TID_MAX),
        )
    )
    log(f"  Dummy users:   {r.rowcount} deleted")

    await session.flush()

    # 14. Recalculate balances for affected REAL users.
    real_affected = [
        uid for uid in affected_uids if uid not in dummy_uids
    ]
    for uid in real_affected:
        user = await session.get(User, uid)
        if user is None:
            continue
        balance = (await session.execute(
            select(func.coalesce(func.sum(UserLedger.amount_cents), 0))
            .where(
                UserLedger.user_id == uid,
                UserLedger.status == LedgerStatus.DONE.value,
            )
        )).scalar_one()
        object.__setattr__(user, "_ledger_update", True)
        user.balance_cents = balance
        object.__setattr__(user, "_ledger_update", False)

    # 15. Recalculate balances for affected REAL masters.
    real_masters_affected = [
        mid for mid in affected_mids if mid not in dummy_uids
    ]
    for mid in real_masters_affected:
        profile = await session.get(MasterProfile, mid)
        if profile is None:
            continue
        frozen, available = await _master_sums(mid, session)
        object.__setattr__(profile, "_ledger_update", True)
        profile.frozen_cents = frozen
        profile.available_cents = available
        object.__setattr__(profile, "_ledger_update", False)

    await session.flush()
    log("Reset complete ✓\n")


async def _master_sums(
    user_id: UUID, session: AsyncSession,
) -> tuple[int, int]:
    """Compute (frozen_cents, available_cents) from master_ledger."""
    stmt = select(
        func.coalesce(
            func.sum(
                case(
                    (MasterLedger.is_frozen.is_(True), MasterLedger.amount_cents),
                    else_=0,
                )
            ), 0,
        ),
        func.coalesce(
            func.sum(
                case(
                    (MasterLedger.is_frozen.is_(False), MasterLedger.amount_cents),
                    else_=0,
                )
            ), 0,
        ),
    ).where(
        MasterLedger.user_id == user_id,
        MasterLedger.status == LedgerStatus.DONE.value,
    )
    row = (await session.execute(stmt)).one()
    return int(row[0]), int(row[1])


# ===================================================================
# User / Master creation
# ===================================================================

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    first_name: str,
    last_name: str | None = None,
    role: UserRole = UserRole.USER,
) -> tuple[User, bool]:
    """Find or create a user by telegram_id. Returns (user, created).

    Role upgrade rules:
      - If existing role < requested role → upgrade silently.
      - If existing role > requested role → warn and keep existing role.
      - Equal → no change.

    Priority order: ADMIN (2) > MASTER (1) > USER (0).
    """
    _ROLE_RANK = {UserRole.USER: 0, UserRole.MASTER: 1, UserRole.ADMIN: 2}

    stmt = select(User).where(User.telegram_id == telegram_id)
    existing = (await session.execute(stmt)).scalar_one_or_none()

    if existing is not None:
        existing_rank = _ROLE_RANK[existing.role]
        requested_rank = _ROLE_RANK[role]

        if existing_rank < requested_rank:
            # Upgrade: USER → MASTER, USER → ADMIN, MASTER → ADMIN.
            existing.role = role
            await session.flush()
            log(f"  User {telegram_id} upgraded: {existing.role} → {role.value}")
        elif existing_rank > requested_rank:
            # Downgrade: warn and keep existing role.
            warn(
                f"User {telegram_id} is already a "
                f"{str(existing.role).upper()} — cannot downgrade to "
                f"{role.value.upper()}. Keeping existing role."
            )
        return existing, False

    user = User(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        role=role,
    )
    session.add(user)
    await session.flush()
    return user, True


async def ensure_master_profile(
    session: AsyncSession,
    user: User,
    display_name: str,
    bio: str,
    methods: list[str] | None = None,
) -> MasterProfile:
    """Create or update a verified MasterProfile."""
    profile = await session.get(MasterProfile, user.id)
    data = {
        "account": {"status": "verified"},
        "profile": {
            "display_name": display_name,
            "bio": bio,
            "methods": methods or [],
        },
        "availability": {"accepting_bookings": True},
        "settings": {"auto_confirm": True, "default_max_participants": 20},
        "stats": {"total_practices": 0, "avg_rating": 0},
    }
    if profile is not None:
        profile.set_jsonb("data", data)
        await session.flush()
        return profile

    profile = MasterProfile(user_id=user.id, data=data)
    session.add(profile)
    await session.flush()
    return profile


# ===================================================================
# Practice creation
# ===================================================================

async def create_seed_practice(
    session: AsyncSession,
    template: dict,
    master_id: UUID,
) -> Practice | None:
    """Create a seed practice. Returns None if already exists."""
    title = template["title"]
    marker_desc = template["description"] + SEED_MARKER

    # Idempotency: check if this practice already exists.
    stmt = select(Practice).where(
        Practice.title == title,
        Practice.description.like(f"%__SEED__%"),
        Practice.master_id == master_id,
    )
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        warn(f"  Practice already exists: {title}")
        return existing

    scheduled_at = NOW + template["offset"]

    practice = Practice(
        master_id=master_id,
        practice_type=template["practice_type"],
        status=template["target_status"],
        title=title,
        description=marker_desc,
        what_to_prepare=template.get("what_to_prepare"),
        contraindications=template.get("contraindications"),
        scheduled_at=scheduled_at,
        duration_minutes=template["duration_minutes"],
        timezone=PRACTICE_TZ,
        max_participants=template["max_participants"],
        is_free=template["is_free"],
        price_cents=template["price_cents"],
        currency="eur",
    )
    session.add(practice)
    await session.flush()
    return practice


# ===================================================================
# Booking + Purchase + Ledger creation
# ===================================================================

async def create_seed_booking(
    session: AsyncSession,
    user: User,
    practice: Practice,
) -> Booking | None:
    """Create booking with purchase and double-entry ledger.

    Handles all practice statuses correctly:
      - scheduled/live: confirmed booking, pending purchase, frozen ledger
      - completed: attended booking, completed purchase, unfrozen + commission
      - free: same flow but all amounts are 0

    Returns None if user is the practice master or already booked.
    """
    # Guard: cannot book own practice.
    if user.id == practice.master_id:
        return None

    # Idempotency: check for existing active booking.
    stmt = select(Booking).where(
        Booking.user_id == user.id,
        Booking.practice_id == practice.id,
        Booking.status != BookingStatus.CANCELLED.value,
    )
    if (await session.execute(stmt)).scalar_one_or_none():
        return None

    is_completed = practice.status == PracticeStatus.COMPLETED.value
    is_live = practice.status == PracticeStatus.LIVE.value
    pid = str(practice.id)

    # -- Booking --
    booking = Booking(
        practice_id=practice.id,
        user_id=user.id,
        status=(
            BookingStatus.ATTENDED.value if is_completed
            else BookingStatus.CONFIRMED.value
        ),
    )
    if is_completed or is_live:
        booking.joined_at = practice.scheduled_at + timedelta(minutes=1)
    if is_completed:
        booking.left_at = (
            practice.scheduled_at
            + timedelta(minutes=practice.duration_minutes)
        )
    session.add(booking)
    await session.flush()

    # -- Purchase --
    commission = 0
    if is_completed:
        commission = (
            practice.price_cents * settings.commission_percent // 100
        )

    purchase = Purchase(
        user_id=user.id,
        practice_id=practice.id,
        booking_id=booking.id,
        amount_cents=practice.price_cents,
        discount_cents=0,
        paid_cents=practice.price_cents,
        currency=practice.currency.lower(),
        commission_cents=commission,
        status=(
            PurchaseStatus.COMPLETED.value if is_completed
            else PurchaseStatus.PENDING.value
        ),
    )
    if is_completed:
        purchase.completed_at = (
            practice.scheduled_at
            + timedelta(minutes=practice.duration_minutes + 5)
        )
    session.add(purchase)
    await session.flush()

    # Link booking -> purchase.
    booking.purchase_id = purchase.id
    await session.flush()

    # -- Double-entry ledger --

    # User debit (always, even free).
    await record_user_ledger(
        user_id=user.id,
        amount_cents=-practice.price_cents,
        reason=f"{SEED_REASON}purchase:practice={pid}",
        session=session,
    )

    if is_completed:
        # Master credit (unfrozen -- practice already completed).
        await record_master_ledger(
            user_id=practice.master_id,
            amount_cents=practice.price_cents,
            reason=f"{SEED_REASON}sale:practice={pid}",
            is_frozen=False,
            practice_id=practice.id,
            session=session,
        )
        # Commission: master debit + company credit.
        if commission > 0:
            await record_master_ledger(
                user_id=practice.master_id,
                amount_cents=-commission,
                reason=f"{SEED_REASON}commission:practice={pid}",
                is_frozen=False,
                practice_id=practice.id,
                session=session,
            )
            await record_company_ledger(
                amount_cents=commission,
                ledger_type=CompanyLedgerType.COMMISSION.value,
                reason=f"{SEED_REASON}commission:practice={pid}",
                reference_id=purchase.id,
                session=session,
            )
        # Audit entry expected by semaphore 5.6 (mirrors finalize_purchases).
        await record_audit(
            event="purchase_completed",
            actor_id=user.id,
            actor_type="user",
            target_type="purchase",
            target_id=purchase.id,
            data={
                "practice_id": pid,
                "paid_cents": purchase.paid_cents,
                "commission_cents": commission,
                "promo_id": None,
            },
            session=session,
        )
    else:
        # Master credit (frozen -- practice pending).
        await record_master_ledger(
            user_id=practice.master_id,
            amount_cents=practice.price_cents,
            reason=f"{SEED_REASON}sale:practice={pid}",
            is_frozen=True,
            practice_id=practice.id,
            session=session,
        )

    return booking


# ===================================================================
# Main seed orchestrator
# ===================================================================

async def seed(reset: bool = False) -> None:
    """Main seed entry point."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            # -- Verify tables exist (migrations must run first) --
            from sqlalchemy import text

            try:
                await session.execute(
                    text("SELECT 1 FROM users LIMIT 1"),
                )
            except Exception:
                await session.rollback()
                err("Tables do not exist. Run migrations first:")
                err("  velo db migrate")
                return

            # -- Reset if requested --
            if reset:
                await reset_seed_data(session)
                await session.commit()

            # -- Interactive input --
            master_tids, user_tids, admin_tids = ask_telegram_ids()

            # ========================================
            # STEP 1: Create users and masters
            # ========================================
            log("Creating users and masters...")

            # Real admins (ADMIN role + MasterProfile).
            all_admins: list[User] = []
            for i, tid in enumerate(admin_tids):
                user, created = await get_or_create_user(
                    session, tid,
                    first_name=f"Админ {i + 1}",
                    role=UserRole.ADMIN,
                )
                await ensure_master_profile(
                    session, user,
                    display_name=user.first_name or f"Админ {i + 1}",
                    bio=(
                        "Администратор платформы. Также ведёт практики "
                        "по медитации и дыхательным техникам."
                    ),
                    methods=["meditation", "breathwork"],
                )
                all_admins.append(user)
                status = "created" if created else "exists"
                log(f"  Admin: tg={tid} ({status})")

            # Real masters.
            all_masters: list[User] = list(all_admins)  # admins are also masters
            for i, tid in enumerate(master_tids):
                user, created = await get_or_create_user(
                    session, tid,
                    first_name=f"Мастер {i + 1}",
                    role=UserRole.MASTER,
                )
                await ensure_master_profile(
                    session, user,
                    display_name=user.first_name or f"Мастер {i + 1}",
                    bio=(
                        "Практик и наставник. Веду занятия по медитации, "
                        "йоге и дыхательным практикам."
                    ),
                    methods=["meditation", "yoga", "breathwork"],
                )
                all_masters.append(user)
                status = "created" if created else "exists"
                log(f"  Master: tg={tid} ({status})")

            # Dummy masters.
            for md in DUMMY_MASTER_DATA:
                user, _ = await get_or_create_user(
                    session, md["tid"],
                    first_name=md["first_name"],
                    last_name=md["last_name"],
                    role=UserRole.MASTER,
                )
                await ensure_master_profile(
                    session, user,
                    display_name=md["display_name"],
                    bio=md["bio"],
                    methods=md["methods"],
                )
                all_masters.append(user)
                log(f"  Master: tg={md['tid']} (dummy: {md['display_name']})")

            # Real users.
            all_users: list[User] = []
            seen_tids: set[int] = set()
            all_master_tids = {m.telegram_id for m in all_masters}
            for i, tid in enumerate(user_tids):
                if tid in all_master_tids:
                    # Already created as master or admin -- reuse.
                    user = next(
                        m for m in all_masters if m.telegram_id == tid
                    )
                    all_users.append(user)
                    log(f"  User: tg={tid} (already {user.role.value}, can book others)")
                    seen_tids.add(tid)
                    continue
                user, created = await get_or_create_user(
                    session, tid,
                    first_name=f"Юзер {i + 1}",
                )
                all_users.append(user)
                seen_tids.add(tid)
                status = "created" if created else "exists"
                log(f"  User: tg={tid} ({status})")

            # Dummy users.
            dummy_users: list[User] = []
            for i, tid in enumerate(range(DUMMY_TID_MIN, DUMMY_TID_MIN + 28)):
                fn, ln = DUMMY_FIRST_NAMES[i]
                user, _ = await get_or_create_user(
                    session, tid,
                    first_name=fn,
                    last_name=ln,
                )
                dummy_users.append(user)
                all_users.append(user)

            log(f"  Created {len(dummy_users)} dummy users (tg={DUMMY_TID_MIN}..)")

            # ========================================
            # STEP 2: Topup balances
            # ========================================
            log("Topping up balances...")

            # Collect all users who need topup (masters + users).
            topup_targets: dict[UUID, int] = {}
            for u in all_users:
                amount = (
                    REAL_USER_TOPUP
                    if u.telegram_id and u.telegram_id < DUMMY_TID_MIN
                    else DUMMY_USER_TOPUP
                )
                topup_targets[u.id] = amount
            # Masters who are NOT in all_users also get topup.
            for m in all_masters:
                if m.id not in topup_targets:
                    amount = (
                        REAL_USER_TOPUP
                        if m.telegram_id and m.telegram_id < DUMMY_TID_MIN
                        else DUMMY_USER_TOPUP
                    )
                    topup_targets[m.id] = amount

            topup_count = 0
            for uid, amount in topup_targets.items():
                # Idempotency: check for existing seed topup.
                stmt = select(UserLedger.id).where(
                    UserLedger.user_id == uid,
                    UserLedger.reason == f"{SEED_REASON}topup",
                ).limit(1)
                if (await session.execute(stmt)).scalar_one_or_none():
                    continue
                await record_user_ledger(
                    user_id=uid,
                    amount_cents=amount,
                    reason=f"{SEED_REASON}topup",
                    session=session,
                )
                # Offsetting company entry: platform received money (liability).
                # Double-entry rule: user(+N) + company(-N) = 0.
                await record_company_ledger(
                    amount_cents=-amount,
                    ledger_type=CompanyLedgerType.TOPUP.value,
                    reason=f"{SEED_REASON}topup",
                    session=session,
                )
                topup_count += 1

            log(f"  Topped up {topup_count} users")

            # ========================================
            # STEP 3: Create practices
            # ========================================
            log("Creating practices...")

            # Build telegram_id -> User lookup for fixed_master_tid templates.
            master_by_tid: dict[int, User] = {
                m.telegram_id: m
                for m in all_masters
                if m.telegram_id is not None
            }

            # practices list mirrors PRACTICE_TEMPLATES indices for STEP 4.
            # Banner templates (seed_for_real_users=True) are included so
            # their index stays aligned with PRACTICE_TEMPLATES.
            practices: list[Practice | None] = []
            for i, tmpl in enumerate(PRACTICE_TEMPLATES):
                # Banner templates: fixed dummy master, not round-robin.
                fixed_tid = tmpl.get("fixed_master_tid")
                if fixed_tid is not None:
                    fixed_master = master_by_tid.get(fixed_tid)
                    if fixed_master is None:
                        warn(
                            f"  fixed_master_tid={fixed_tid} not found "
                            f"-- skipping banner practice '{tmpl['title']}'"
                        )
                        practices.append(None)
                        continue
                    master = fixed_master
                else:
                    master = all_masters[i % len(all_masters)]

                p = await create_seed_practice(session, tmpl, master.id)
                practices.append(p)
                if p is not None:
                    status_icon = {
                        PracticeStatus.SCHEDULED.value: "📅",
                        PracticeStatus.LIVE.value: "🔴",
                        PracticeStatus.COMPLETED.value: "✅",
                        PracticeStatus.CANCELLED.value: "❌",
                    }.get(p.status, "❓")
                    banner_tag = " [BANNER]" if tmpl.get("seed_for_real_users") else ""
                    price = (
                        "free" if p.is_free
                        else f"€{p.price_cents / 100:.2f}"
                    )
                    log(f"  {status_icon} {p.title} ({price}){banner_tag}")

            # ========================================
            # STEP 4: Create bookings
            # ========================================
            log("Creating bookings...")

            # All real users across all roles -- used for banner bookings.
            # Deduped by user.id (same person may appear in multiple role lists).
            real_users_all: list[User] = list(
                {u.id: u for u in all_users + all_masters + all_admins}.values()
            )

            total_bookings = 0
            for i, tmpl in enumerate(PRACTICE_TEMPLATES):
                if i >= len(practices):
                    break
                practice = practices[i]
                if practice is None:
                    continue

                # Banner template: book every real user regardless of num_bookings.
                if tmpl.get("seed_for_real_users"):
                    candidates = [
                        u for u in real_users_all
                        if u.id != practice.master_id
                        and u.telegram_id is not None
                        and u.telegram_id > DUMMY_TID_MAX
                    ]
                    booked = 0
                    for user in candidates:
                        b = await create_seed_booking(session, user, practice)
                        if b is not None:
                            booked += 1
                            total_bookings += 1
                    if booked > 0:
                        await recalculate_participants(practice.id, session)
                    log(f"  Banner '{practice.title}': {booked} real-user bookings")
                    continue

                num = tmpl["num_bookings"]
                if num == 0:
                    continue

                # Standard template: real users first, then dummies.
                real_eligible = [
                    u for u in all_users
                    if u.id != practice.master_id
                    and u.telegram_id is not None
                    and u.telegram_id < DUMMY_TID_MIN
                ]
                dummy_eligible = [
                    u for u in dummy_users
                    if u.id != practice.master_id
                ]
                # Also include real masters who are not this practice's master.
                master_eligible = [
                    m for m in all_masters
                    if m.id != practice.master_id
                    and m.telegram_id is not None
                    and m.telegram_id < DUMMY_TID_MIN
                    and m not in real_eligible
                ]

                candidates = real_eligible + master_eligible + dummy_eligible
                booked = 0
                for user in candidates:
                    if booked >= num:
                        break
                    b = await create_seed_booking(session, user, practice)
                    if b is not None:
                        booked += 1
                        total_bookings += 1

                # Recalculate participant count.
                if booked > 0:
                    await recalculate_participants(practice.id, session)

            log(f"  Created {total_bookings} bookings with purchases + ledger")

            # ========================================
            # STEP 5: Commit
            # ========================================
            await session.commit()

            # -- Summary --
            print(f"\n{G}{'=' * 55}{N}")
            print(f"{G}  VELO Seed Complete ✓{N}")
            print(f"{G}{'=' * 55}{N}")
            print(f"  Admins:     {len(all_admins)}")
            print(f"  Masters:    {len(all_masters)}")
            print(f"  Users:      {len(all_users)}")
            print(f"  Practices:  {len(practices)}")
            print(f"  Bookings:   {total_bookings}")
            print()

        except Exception as exc:
            await session.rollback()
            err(f"Seed failed: {exc}")
            raise
        finally:
            await dispose_engine()


# ===================================================================
# Entry point
# ===================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VELO -- Seed database with test data",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clean all seed data before re-seeding",
    )
    args = parser.parse_args()
    asyncio.run(seed(reset=args.reset))


if __name__ == "__main__":
    main()
