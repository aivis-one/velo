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
#   - Diary timeline events (DiaryEvent journal) for real users -- projected
#     via diary/projections.py so they show up in GET /diary/feed: bookings,
#     practice outcomes (attended + no_show), check-ins, feedbacks, and
#     personal note/dream entries spread across several calendar days
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

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditLog, record_audit
from app.core.config import settings
from app.core.database import dispose_engine, get_session_factory
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.bookings.service import recalculate_participants
from app.modules.diary.models import (
    Checkin,
    CheckType,
    DiaryEntry,
    DiaryEntryType,
    DiaryEvent,
    Feedback,
)
from app.modules.diary.projections import (
    project_booking_cancelled,
    project_booking_confirmed,
    project_practice_outcome,
    upsert_checkin_event,
    upsert_entry_event,
    upsert_feedback_event,
)
from app.modules.masters.models import MasterProfile
from app.modules.masters.service import get_master_display_name
from app.modules.notifications.models import Notification, NotificationDelivery
from app.modules.payments.models import (
    CompanyLedger,
    CompanyLedgerType,
    MasterLedger,
    Payment,
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
from app.modules.promos.models import Promo
from app.modules.reports.models import Report
from app.modules.users.models import User, UserRole
from app.modules.waitlist.models import Waitlist
from app.modules.withdrawals.models import Withdrawal


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
        "direction": "meditation",
        "difficulty": "beginner",
        "style": None,
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
        "direction": "yoga",
        "difficulty": "beginner",
        "style": "vinyasa",
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
        "direction": "breathwork",
        "difficulty": "medium",
        "style": None,
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
        "direction": "meditation",
        "difficulty": "beginner",
        "style": None,
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
        "direction": "yoga",
        "difficulty": "beginner",
        "style": "yin",
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
        "direction": "meditation",
        "difficulty": "medium",
        "style": None,
        "target_status": PracticeStatus.LIVE.value,
        "duration_minutes": 60,
        "max_participants": 20,
        "is_free": False,
        "price_cents": 1200,
        "offset": timedelta(minutes=-30),
        "num_bookings": 7,
        # Real users must not be booked here: an in-progress LIVE practice
        # would otherwise win "nearest practice" on the dashboard over the
        # check-in banner (#12). Dummy users fill the seats instead.
        "skip_real_users": True,
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
        "direction": "yoga",
        "difficulty": "medium",
        "style": "hatha",
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
        "direction": "meditation",
        "difficulty": "beginner",
        "style": "yin",
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
        "direction": "breathwork",
        "difficulty": "medium",
        "style": "hatha",
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
        "direction": "yoga",
        "difficulty": "high",
        "style": "kundalini",
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
        "direction": "meditation",
        "difficulty": "medium",
        "style": None,
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
        "direction": "meditation",
        "difficulty": "high",
        "style": None,
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
        "direction": "meditation",
        "difficulty": "beginner",
        "style": None,
        "target_status": PracticeStatus.SCHEDULED.value,
        "duration_minutes": 45,
        "max_participants": 100,
        "is_free": True,
        "price_cents": 0,
        "offset": timedelta(minutes=90),
        "num_bookings": 0,
        "seed_for_real_users": True,
        "fixed_master_tid": 9900029,
        "zoom_link": "https://us02web.zoom.us/j/0000000012",
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
        "direction": "meditation",
        "difficulty": "beginner",
        "style": None,
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
    # -- 14: BANNER -- live now (confirmed booking for all real users) --
    # scheduled_at = NOW - 10 min, duration 60 -> currently in progress.
    # Gives the Practice-Live screen (14) real data: a joined booking + zoom.
    # Owner is DUMMY_MASTER_DATA[0] (Елена Мирная, tid=9900029).
    {
        "title": "Дневная практика (эфир)",
        "description": (
            "Практика идёт прямо сейчас. "
            "Подключайтесь к эфиру и присоединяйтесь к группе."
        ),
        "what_to_prepare": "Удобная одежда, коврик, вода.",
        "contraindications": None,
        "practice_type": PracticeType.LIVE.value,
        "direction": "meditation",
        "difficulty": "beginner",
        "style": None,
        "target_status": PracticeStatus.LIVE.value,
        "duration_minutes": 60,
        "max_participants": 100,
        "is_free": False,
        "price_cents": 800,
        "offset": timedelta(minutes=-10),
        "num_bookings": 0,
        "seed_for_real_users": True,
        "fixed_master_tid": 9900029,
        "zoom_link": "https://us02web.zoom.us/j/0000000014",
    },
]


# ===================================================================
# Real-user journey practices (Phase: flow 10-18 enrichment)
# ===================================================================
#
# These are COMPLETED practices in the past, owned by a dummy master,
# booked as ATTENDED by every real user. Each one also seeds a check-in
# (mood) and a feedback (rating), with comments on roughly half of them.
#
# Goal: a rich, varied history so the dashboard "progress" looks full and
# the diary / insights / AI mood indicator have all states represented.
# All 9 mood x rating combinations are covered across the list.
#
# owner: DUMMY_MASTER_DATA[0] (Елена Мирная, tid=9900029).
# Durations are chosen so total practice hours land around 9-10h here, and
# comfortably above the mockup's "12 / 9,5" once the standard completed
# templates (#6-9) the user also attends are added on top.
JOURNEY_MASTER_TID = 9900029

JOURNEY_PRACTICES: list[dict] = [
    {
        "title": "Хатха-йога: утренний поток",
        "description": "Мягкое пробуждение тела через классические асаны.",
        "what_to_prepare": "Коврик, удобная одежда.",
        "duration_minutes": 60,
        "offset": timedelta(days=-2, hours=8),
        "mood": 9, "rating": 9,
        "checkin_comment": "Проснулась с лёгкостью, настроена на практику.",
        "feedback_comment": "Прекрасное начало дня, чувствую прилив сил!",
    },
    {
        "title": "Медитация осознанности",
        "description": "Наблюдение за дыханием и телесными ощущениями.",
        "what_to_prepare": "Подушка для медитации.",
        "duration_minutes": 45,
        "offset": timedelta(days=-4, hours=19),
        "mood": 6, "rating": 6,
        "checkin_comment": None,
        "feedback_comment": None,
    },
    {
        "title": "Дыхание нади-шодхана",
        "description": "Попеременное дыхание для баланса нервной системы.",
        "what_to_prepare": "Тихое место, прямая спина.",
        "duration_minutes": 30,
        "offset": timedelta(days=-6, hours=7),
        "mood": 2, "rating": 2,
        "checkin_comment": "Чувствую тревогу, тяжело сосредоточиться.",
        "feedback_comment": "Не до конца поняла технику, нужно повторить.",
    },
    {
        "title": "Йога-нидра: глубокий отдых",
        "description": "Осознанное расслабление лёжа.",
        "what_to_prepare": "Плед, маска для сна.",
        "duration_minutes": 45,
        "offset": timedelta(days=-9, hours=21),
        "mood": 9, "rating": 6,
        "checkin_comment": None,
        "feedback_comment": None,
    },
    {
        "title": "Звуковая медитация с чашами",
        "description": "Вибрации поющих чаш для глубокого покоя.",
        "what_to_prepare": "Коврик, плед.",
        "duration_minutes": 60,
        "offset": timedelta(days=-12, hours=18),
        "mood": 6, "rating": 9,
        "checkin_comment": "День был насыщенный, хочу расслабиться.",
        "feedback_comment": "Невероятно глубокое погружение, всё тело отдохнуло.",
    },
    {
        "title": "Виньяса флоу",
        "description": "Динамичная последовательность асан в ритме дыхания.",
        "what_to_prepare": "Коврик, вода.",
        "duration_minutes": 60,
        "offset": timedelta(days=-16, hours=9),
        "mood": 2, "rating": 9,
        "checkin_comment": None,
        "feedback_comment": None,
    },
    {
        "title": "Метта-медитация любящей доброты",
        "description": "Культивирование сострадания к себе и другим.",
        "what_to_prepare": "Удобное сидячее положение.",
        "duration_minutes": 30,
        "offset": timedelta(days=-20, hours=20),
        "mood": 2, "rating": 6,
        "checkin_comment": "Грустное настроение, нужна поддержка.",
        "feedback_comment": "Стало теплее на душе, спасибо.",
    },
    {
        "title": "Кундалини: набхи-крия",
        "description": "Работа с энергией пупочного центра.",
        "what_to_prepare": "Белая одежда, коврик.",
        "duration_minutes": 75,
        "offset": timedelta(days=-25, hours=10),
        "mood": 6, "rating": 2,
        "checkin_comment": None,
        "feedback_comment": None,
    },
    {
        "title": "Растяжка и релакс",
        "description": "Мягкое вытяжение и снятие напряжения.",
        "what_to_prepare": "Коврик, ремень для йоги.",
        "duration_minutes": 45,
        "offset": timedelta(days=-30, hours=18),
        "mood": 9, "rating": 2,
        "checkin_comment": "Спина устала за неделю, нужна растяжка.",
        "feedback_comment": "Хорошо потянулась, но местами было непонятно.",
    },
    {
        "title": "Вечерняя практика покоя",
        "description": "Подготовка ко сну: дыхание и расслабление.",
        "what_to_prepare": "Плед, приглушённый свет.",
        "duration_minutes": 30,
        "offset": timedelta(days=-40, hours=22),
        "mood": 6, "rating": 6,
        "checkin_comment": None,
        "feedback_comment": None,
    },
]


# ===================================================================
# Personal diary entries (note / dream) for the unified feed
# ===================================================================
#
# Standalone journal entries (NOT tied to a practice) seeded onto every real
# user's timeline. They give the feed its note ("Дневник") and dream
# ("Сонник") cards -- the standard-card form the practice-derived events do
# not produce -- and spread across a few calendar days so the date-nodes and
# left/right alternation are visible. created_at is backdated (the projection
# takes the event occurred_at from entry.created_at).
DIARY_ENTRY_TEMPLATES: list[dict] = [
    {
        "entry_type": DiaryEntryType.NOTE.value,
        "title": "Мысли после недели практик",
        "content": (
            "Замечаю, что стал спокойнее реагировать на мелкие раздражители. "
            "Утренняя медитация явно держит фон ровнее в течение дня."
        ),
        "mood": 9,
        "offset": timedelta(days=-1, hours=21),
    },
    {
        "entry_type": DiaryEntryType.DREAM.value,
        "title": "Сон про полёт над морем",
        "content": (
            "Снилось, будто лечу низко над водой, чувствую брызги и ветер. "
            "Совсем не страшно -- наоборот, спокойствие и лёгкость."
        ),
        "mood": 6,
        "offset": timedelta(days=-1, hours=7),
    },
    {
        "entry_type": DiaryEntryType.NOTE.value,
        "title": "Короткая запись дня",
        "content": (
            "День выдался суматошный, но вечерняя практика помогла собраться "
            "и отпустить лишнее."
        ),
        "mood": 6,
        "offset": timedelta(days=-3, hours=22),
    },
    {
        "entry_type": DiaryEntryType.DREAM.value,
        "title": "Странный сон с лабиринтом",
        "content": (
            "Долго блуждал по бесконечным коридорам в поисках выхода. "
            "Проснулся с ощущением, что что-то важное осталось недосказанным."
        ),
        "mood": None,
        "offset": timedelta(days=-5, hours=6),
    },
    {
        "entry_type": DiaryEntryType.NOTE.value,
        "title": "Намерение на месяц",
        "content": (
            "Хочу довести до автоматизма утреннюю практику и добавить короткую "
            "дыхательную сессию перед сном."
        ),
        "mood": 9,
        "offset": timedelta(days=-8, hours=20),
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

async def wipe_all_data(session: AsyncSession) -> None:
    """Delete ALL rows from ALL domain tables (full database wipe).

    Test server only -- we do NOT preserve data. This drops every row so
    the subsequent seed recreates everything from scratch, including real
    users (so their role is set exactly per the interactive input, with no
    "role can only go up" stickiness).

    Deletion order is FK-safe and mirrors tests/helpers.full_cleanup_range:
    children before parents, financial RESTRICT tables (purchases, payments)
    before bookings/users. ORM deletes only -- no raw SQL (project rule).
    """
    log("Wiping ALL data (full reset)...")

    # Order matters -- delete children before parents.
    # 1. Notifications (deliveries -> notifications).
    await session.execute(delete(NotificationDelivery))
    await session.execute(delete(Notification))

    # 2. Diary: timeline journal first, then check-ins, feedbacks, entries.
    # DiaryEvent.user_id is ON DELETE CASCADE, but we delete it explicitly
    # (same pattern as the rest of this wipe) so a re-seed starts clean.
    await session.execute(delete(DiaryEvent))
    await session.execute(delete(Checkin))
    await session.execute(delete(Feedback))
    await session.execute(delete(DiaryEntry))

    # 3. Audit logs (FK -> users.actor_id).
    await session.execute(delete(AuditLog))

    # 4. Ledgers (no hard FK to users, but conceptually downstream).
    await session.execute(delete(CompanyLedger))
    await session.execute(delete(MasterLedger))
    await session.execute(delete(UserLedger))

    # 5. Financial RESTRICT tables -- MUST precede bookings / users.
    await session.execute(delete(Payment))
    await session.execute(delete(Purchase))

    # 6. Booking-adjacent domain tables.
    await session.execute(delete(Waitlist))
    await session.execute(delete(Booking))
    await session.execute(delete(Withdrawal))
    await session.execute(delete(Report))
    await session.execute(delete(Promo))

    # 7. Practices and master profiles (FK -> users).
    await session.execute(delete(Practice))
    await session.execute(delete(MasterProfile))

    # 8. Users (parent of almost everything).
    await session.execute(delete(User))

    await session.flush()
    log("Wipe complete -- database is empty\n")


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
        zoom_link=template.get("zoom_link"),
    )

    # Calendar taxonomy -> data.taxonomy (JSONB sandbox). Written the SAME way
    # as the production service (practices/service.py create_practice): via
    # set_jsonb so the structure matches what list_public_practices filters on
    # (data['taxonomy']['direction'] ->> ...). Templates that omit the fields
    # fall back to meditation/beginner so a practice is never left untaxonomied.
    practice.set_jsonb(
        "data",
        {
            "taxonomy": {
                "direction": template.get("direction", "meditation"),
                "difficulty": template.get("difficulty", "beginner"),
                "style": template.get("style"),
            },
        },
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
# Diary creation (check-in + feedback) -- direct insert, bypassing
# API time-window validation (mirrors tests/test_insights helper).
# ===================================================================

async def create_seed_diary(
    session: AsyncSession,
    booking: Booking,
    practice: Practice,
    *,
    mood: str,
    rating: str | None = None,
    checkin_comment: str | None = None,
    feedback_comment: str | None = None,
) -> None:
    """Seed a check-in (and optionally a feedback) for a booking.

    - Check-in (PRE) is created for any booking with a mood.
    - Feedback is created only when a rating is given AND the practice is
      completed (matches the real feedback condition: attended + completed).
    - Comments are written only when non-empty (model requires min_length=1).
    - Idempotent: skips if a matching row already exists.

    DIARY FEED (redesign): after creating each source row we project it onto
    the timeline journal via the SAME upsert_* functions production uses
    (diary/service.py), so the row shows up in GET /diary/feed. The projection
    reads occurred_at from the source's created_at, so we backdate created_at:
    the check-in lands just before the practice, the feedback just after it.
    Both are clamped to NOW so future / live practices (banner check-ins)
    never project an event with a future timestamp. All callers pass real
    users, so projecting unconditionally here is fine.
    """
    # Master display name for the snapshot (one lookup, reused below).
    master_name = await get_master_display_name(practice.master_id, session)

    # -- Check-in (one PRE per booking) --
    existing_checkin = (
        await session.execute(
            select(Checkin).where(
                Checkin.booking_id == booking.id,
                Checkin.check_type == CheckType.PRE.value,
            )
        )
    ).scalar_one_or_none()
    if existing_checkin is None:
        checkin = Checkin(
            practice_id=practice.id,
            user_id=booking.user_id,
            booking_id=booking.id,
            mood=mood,
            comment=checkin_comment or None,
            check_type=CheckType.PRE.value,
        )
        # Backdate so the projected event sits on the practice's day, just
        # before it; clamp to NOW for future / live practices.
        checkin.created_at = min(
            practice.scheduled_at - timedelta(minutes=30), NOW,
        )
        session.add(checkin)
        await session.flush()

        # Diary feed projection (occurred_at = checkin.created_at).
        await upsert_checkin_event(
            session,
            checkin=checkin,
            practice=practice,
            master_name=master_name,
        )

    # -- Feedback (one per practice+user, only for completed practices) --
    if rating is not None and practice.status == PracticeStatus.COMPLETED.value:
        existing_feedback = (
            await session.execute(
                select(Feedback).where(
                    Feedback.practice_id == practice.id,
                    Feedback.user_id == booking.user_id,
                )
            )
        ).scalar_one_or_none()
        if existing_feedback is None:
            feedback = Feedback(
                practice_id=practice.id,
                user_id=booking.user_id,
                booking_id=booking.id,
                rating=rating,
                comment=feedback_comment or None,
            )
            # Backdate to just after the practice ended; clamp to NOW.
            feedback.created_at = min(
                practice.scheduled_at
                + timedelta(minutes=practice.duration_minutes + 15),
                NOW,
            )
            session.add(feedback)
            await session.flush()

            # Diary feed projection (occurred_at = feedback.created_at).
            await upsert_feedback_event(
                session,
                feedback=feedback,
                practice=practice,
                master_name=master_name,
            )


# ===================================================================
# Diary feed projections for seeded bookings (redesign)
# ===================================================================

async def project_seed_booking_events(
    session: AsyncSession,
    booking: Booking,
    practice: Practice,
    *,
    outcome_status: str | None = None,
) -> None:
    """Project the timeline events for a freshly seeded booking.

    Mirrors the production projection sites (bookings/service.py):
      - booking_confirmed: always, occurred_at set just before the practice
        (the seeded booking has no realistic created_at to reuse, so we pass
        an explicit time -- the projection accepts occurred_at directly).
      - practice_outcome: only when the booking is finalized, with the given
        status (attended / no_show), occurred_at at the practice end.

    Call ONLY for newly created bookings of real users: the per-fact kinds are
    append-only, so re-projecting on a re-run would duplicate rows. The journey
    callers gate on `create_seed_booking(...) is not None` (a fresh booking).
    """
    master_name = await get_master_display_name(practice.master_id, session)

    booked_at = min(practice.scheduled_at - timedelta(hours=2), NOW)
    await project_booking_confirmed(
        session,
        booking=booking,
        practice=practice,
        master_name=master_name,
        occurred_at=booked_at,
    )

    if outcome_status is not None:
        ended_at = min(
            practice.scheduled_at
            + timedelta(minutes=practice.duration_minutes),
            NOW,
        )
        await project_practice_outcome(
            session,
            practice=practice,
            master_name=master_name,
            outcomes=[(booking.user_id, booking.id, outcome_status)],
            occurred_at=ended_at,
        )


async def create_seed_diary_entries(
    session: AsyncSession,
    user: User,
) -> int:
    """Seed standalone diary entries (note / dream) onto a real user's feed.

    Each entry is created directly with a backdated created_at, then projected
    via upsert_entry_event (the same path diary/service.py uses), so it lands
    in the timeline journal on the right day. These give the feed its note
    ("Дневник") and dream ("Сонник") cards. Idempotent: skips an entry whose
    (user, title, type) already exists. Returns the number of entries created.
    """
    created = 0
    for tmpl in DIARY_ENTRY_TEMPLATES:
        exists = (
            await session.execute(
                select(DiaryEntry.id).where(
                    DiaryEntry.user_id == user.id,
                    DiaryEntry.title == tmpl["title"],
                    DiaryEntry.entry_type == tmpl["entry_type"],
                ).limit(1)
            )
        ).scalar_one_or_none()
        if exists is not None:
            continue

        entry = DiaryEntry(
            user_id=user.id,
            entry_type=tmpl["entry_type"],
            title=tmpl["title"],
            content=tmpl["content"],
            mood=tmpl.get("mood"),
        )
        # Backdate so the projected event's occurred_at lands on the chosen
        # day (the projection takes occurred_at from entry.created_at).
        entry.created_at = NOW + tmpl["offset"]
        session.add(entry)
        await session.flush()

        await upsert_entry_event(session, entry=entry)
        created += 1

    return created


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

            # -- Reset if requested: FULL database wipe (test server) --
            if reset:
                await wipe_all_data(session)
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

                # skip_real_users: only dummy users may be booked here
                # (e.g. an in-progress LIVE practice that must not become the
                # dashboard "nearest practice" for a real user).
                skip_real = tmpl.get("skip_real_users", False)

                # Standard template: real users first, then dummies.
                real_eligible = [
                    u for u in all_users
                    if u.id != practice.master_id
                    and u.telegram_id is not None
                    and u.telegram_id < DUMMY_TID_MIN
                ] if not skip_real else []
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
                ] if not skip_real else []

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
            # STEP 4.5: Real-user journey (flow 10-18 enrichment)
            # ========================================
            log("Seeding real-user journey (history + diary + statuses)...")

            # Real users only (exclude dummies). These are the people who will
            # actually open the app and need a rich, varied history. Real
            # Telegram IDs are large, so "real" == above the dummy range
            # (matches the banner-booking predicate; the dummy range is
            # 9900001..9900030).
            journey_users = [
                u for u in all_users
                if u.telegram_id is not None
                and u.telegram_id > DUMMY_TID_MAX
            ]

            journey_master = master_by_tid.get(JOURNEY_MASTER_TID)
            if journey_master is None:
                warn(
                    f"  journey master tid={JOURNEY_MASTER_TID} not found "
                    f"-- skipping journey enrichment"
                )
            elif not journey_users:
                log("  No real users -- skipping journey enrichment")
            else:
                # -- Create journey practices once (owned by dummy master) --
                journey_practices: list[tuple[Practice, dict]] = []
                for jt in JOURNEY_PRACTICES:
                    tmpl = {
                        "title": jt["title"],
                        "description": jt["description"],
                        "what_to_prepare": jt.get("what_to_prepare"),
                        "contraindications": jt.get("contraindications"),
                        "practice_type": PracticeType.LIVE.value,
                        "target_status": PracticeStatus.COMPLETED.value,
                        "duration_minutes": jt["duration_minutes"],
                        "max_participants": 50,
                        "is_free": True,
                        "price_cents": 0,
                        "offset": jt["offset"],
                    }
                    p = await create_seed_practice(
                        session, tmpl, journey_master.id,
                    )
                    if p is not None:
                        journey_practices.append((p, jt))

                # -- One extra future practice to CANCEL (badge "Отменена") --
                cancel_tmpl = {
                    "title": "Отменённое бронирование (демо)",
                    "description": "Практика для демонстрации статуса отмены.",
                    "what_to_prepare": None,
                    "contraindications": None,
                    "practice_type": PracticeType.LIVE.value,
                    "target_status": PracticeStatus.SCHEDULED.value,
                    "duration_minutes": 60,
                    "max_participants": 50,
                    "is_free": False,
                    "price_cents": 1000,
                    "offset": timedelta(days=6, hours=12),
                    "zoom_link": "https://us02web.zoom.us/j/0000000099",
                }
                cancel_practice = await create_seed_practice(
                    session, cancel_tmpl, journey_master.id,
                )

                # -- One extra past practice for NO_SHOW status --
                noshow_tmpl = {
                    "title": "Пропущенная практика (демо)",
                    "description": "Практика для демонстрации статуса 'не пришёл'.",
                    "what_to_prepare": None,
                    "contraindications": None,
                    "practice_type": PracticeType.LIVE.value,
                    "target_status": PracticeStatus.COMPLETED.value,
                    "duration_minutes": 45,
                    "max_participants": 50,
                    "is_free": True,
                    "price_cents": 0,
                    "offset": timedelta(days=-5, hours=18),
                }
                noshow_practice = await create_seed_practice(
                    session, noshow_tmpl, journey_master.id,
                )

                journey_bookings = 0
                journey_diary = 0

                for user in journey_users:
                    # 1. Journey practices: attended booking + checkin + feedback.
                    for practice, jt in journey_practices:
                        b = await create_seed_booking(session, user, practice)
                        if b is not None:
                            journey_bookings += 1
                            # Diary feed: booking_confirmed + attended outcome.
                            await project_seed_booking_events(
                                session, b, practice,
                                outcome_status=BookingStatus.ATTENDED.value,
                            )
                            await create_seed_diary(
                                session, b, practice,
                                mood=jt["mood"],
                                rating=jt["rating"],
                                checkin_comment=jt.get("checkin_comment"),
                                feedback_comment=jt.get("feedback_comment"),
                            )
                            journey_diary += 1

                    # 2. Cancelled booking (badge "Отменена" on screen 17).
                    if cancel_practice is not None:
                        cb = await create_seed_booking(
                            session, user, cancel_practice,
                        )
                        if cb is not None:
                            cb.status = BookingStatus.CANCELLED.value
                            cb.cancelled_at = NOW - timedelta(days=1)
                            cb.cancellation_reason = "Не смогу присутствовать"
                            await session.flush()
                            journey_bookings += 1
                            # Diary feed: honest chronology -- confirmed first,
                            # then cancelled (two rows). Confirm strictly before
                            # the cancel instant (cancel_practice is in the
                            # future, so a generic "2h before" would clamp to
                            # NOW and land after the cancel).
                            cancel_master = await get_master_display_name(
                                cancel_practice.master_id, session,
                            )
                            await project_booking_confirmed(
                                session,
                                booking=cb,
                                practice=cancel_practice,
                                master_name=cancel_master,
                                occurred_at=cb.cancelled_at - timedelta(days=1),
                            )
                            await project_booking_cancelled(
                                session,
                                booking=cb,
                                practice=cancel_practice,
                                master_name=cancel_master,
                                occurred_at=cb.cancelled_at,
                            )

                    # 3. No-show booking (attended-window missed).
                    if noshow_practice is not None:
                        nb = await create_seed_booking(
                            session, user, noshow_practice,
                        )
                        if nb is not None:
                            nb.status = BookingStatus.NO_SHOW.value
                            nb.joined_at = None
                            nb.left_at = None
                            await session.flush()
                            journey_bookings += 1
                            # Diary feed: booking_confirmed + no_show outcome.
                            await project_seed_booking_events(
                                session, nb, noshow_practice,
                                outcome_status=BookingStatus.NO_SHOW.value,
                            )

                    # 4. Personal diary entries (note / dream) for the feed.
                    journey_diary += await create_seed_diary_entries(
                        session, user,
                    )

                # 5. Diary on the LIVE banner practice only (#14).
                #
                # The dashboard shows a "Пора на check-in!" banner for #12 and
                # an "Оставьте feedback!" banner for #13 -- those practices
                # exist to DEMO those prompts. The banners hide once the action
                # is done (has_checkin / has_feedback), so we must NOT pre-seed
                # the prompted action here, or the banner never appears:
                #   - #12 "Утренняя медитация": no check-in -> check-in banner.
                #   - #13 "Вечерняя медитация": no feedback -> feedback banner
                #     (a PRE check-in is fine -- it does not affect that banner).
                # #14 "Дневная практика (эфир)" is the live-now demo and drives
                # no check-in/feedback banner, so its check-in stays for feed
                # variety.
                banner_titles_moods = {
                    "Вечерняя медитация": ("high", None, None, None),
                    "Дневная практика (эфир)": ("mid", None, None, None),
                }
                for practice, _tmpl in (
                    (p, t) for p, t in zip(practices, PRACTICE_TEMPLATES)
                    if p is not None
                ):
                    spec = banner_titles_moods.get(practice.title)
                    if spec is None:
                        continue
                    mood, rating, ci_c, fb_c = spec
                    for user in journey_users:
                        bk = (
                            await session.execute(
                                select(Booking).where(
                                    Booking.user_id == user.id,
                                    Booking.practice_id == practice.id,
                                    Booking.status != BookingStatus.CANCELLED.value,
                                )
                            )
                        ).scalar_one_or_none()
                        if bk is None:
                            continue
                        await create_seed_diary(
                            session, bk, practice,
                            mood=mood, rating=rating,
                            checkin_comment=ci_c, feedback_comment=fb_c,
                        )
                        journey_diary += 1

                # Recalculate participants for journey/cancel/noshow practices.
                for practice, _jt in journey_practices:
                    await recalculate_participants(practice.id, session)
                if cancel_practice is not None:
                    await recalculate_participants(cancel_practice.id, session)
                if noshow_practice is not None:
                    await recalculate_participants(noshow_practice.id, session)

                total_bookings += journey_bookings
                log(
                    f"  Journey: {journey_bookings} bookings, "
                    f"{journey_diary} diary records "
                    f"for {len(journey_users)} real user(s)"
                )

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
