# YON Master Rooms — Architecture Specification v2

**Version:** 2.0  
**Date:** December 26, 2025  
**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, PostgreSQL, Redis, APScheduler  
**Authentication:** Telegram-based (no JWT MVP)

---

## Executive Summary

Переработанная архитектура Master Rooms с учётом:
- ✅ Telegram-аутентификация (без JWT на MVP)
- ✅ Микросервисная архитектура сразу
- ✅ APScheduler для календаря
- ✅ Квизы до/после практик
- ✅ Нотификации: Telegram (личка + каналы/группы)
- ✅ ORM SQLAlchemy 2.0
- ✅ Zoom интеграция (не собственное видео)

---

## Microservices Architecture

```
API Gateway (Kong/Traefik)
  │
  ├─ User Service        (Telegram auth, profiles, masters)
  ├─ Practice Service    (CRUD практик, Zoom integration)
  ├─ Quiz Service        (Pre/Post практики квизы)
  ├─ Calendar Service    (APScheduler, reminders, recurring)
  ├─ Notification Service (Telegram: user/channel/group)
  ├─ Booking Service     (Резервирование мест)
  ├─ Payment Service     (Stripe, subscriptions)
  ├─ State Service       (Check-ins, YON State Engine)
  └─ Library Service     (Записи практик, S3/CDN)
```

---

## Service Responsibilities

### 1. **User Service** — Identity & Profiles
- Telegram authentication (MIXIN pattern for future platforms)
- User profiles (clients)
- Master profiles (approach, certifications, stats)

### 2. **Practice Service** — Practice Management
- CRUD практик (Live, Series, 1:1, Replay)
- Zoom integration (create meetings, get join URLs)
- Practice lifecycle (draft → scheduled → live → completed)

### 3. **Quiz Service** — Pre/Post Practice Quizzes
- Quiz templates (создание мастерами)
- Pre-practice quizzes (check-in: "Как ты себя чувствуешь?")
- Post-practice quizzes (рефлексия: "Как изменилось состояние?")
- Aggregated results для мастера (anonymous)

### 4. **Calendar Service** — Scheduling & Reminders
- APScheduler для управления расписанием
- Auto-reminders (24h, 1h, 10min before practice)
- Recurring practices (series: weekly, monthly)
- Timezone-aware scheduling

### 5. **Notification Service** — Multi-channel Notifications
- Telegram (personal messages, channels, groups/threads)
- Queue management (priority-based)
- Template rendering (Jinja2)
- Delivery tracking

### 6. **Booking Service** — Reservations & Access
- Бронирование мест в практиках
- Access control (кто может join)
- Waitlist (если практика заполнена)
- Attendance tracking

### 7. **Payment Service** — Billing & Subscriptions
- Stripe integration
- Subscriptions (monthly/yearly membership)
- One-time payments (для платных практик)
- Payouts для мастеров

### 8. **State Service** — User States & AI Integration
- Check-ins/Check-outs (состояния до/после)
- Aggregated group state для мастера
- Integration with YON State Engine (external API)

### 9. **Library Service** — Recordings & Content
- Хранение записей практик (S3/CDN)
- Tags и метаданные
- Search & filtering
- Access control (subscription-based)

---

## Database Schemas (SQLAlchemy 2.0)

### User Service Schema

```python
# models/user.py (SQLAlchemy 2.0 ORM)

from sqlalchemy import String, Integer, Boolean, DateTime, JSON, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import UUID, uuid4
import enum

class UserRole(str, enum.Enum):
    CLIENT = "client"
    MASTER = "master"
    ADMIN = "admin"

class AuthPlatform(str, enum.Enum):
    TELEGRAM = "telegram"
    WEB = "web"          # Future
    DISCORD = "discord"  # Future


class User(Base):
    __tablename__ = 'users'
    
    # Identity
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    role: Mapped[UserRole] = mapped_column(default=UserRole.CLIENT)
    
    # Platform MIXIN (telegram_id is primary for MVP)
    auth_platform: Mapped[AuthPlatform] = mapped_column(default=AuthPlatform.TELEGRAM)
    telegram_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    telegram_username: Mapped[str | None] = mapped_column(String(255))
    
    # Future platforms (NULL for MVP)
    web_email: Mapped[str | None] = mapped_column(String(255), unique=True)
    web_password_hash: Mapped[str | None] = mapped_column(String(255))
    discord_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    
    # Profile
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    timezone: Mapped[str] = mapped_column(String(50), default='UTC')
    language: Mapped[str] = mapped_column(String(5), default='en')
    
    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    last_login_at: Mapped[datetime | None]
    
    # Relationships
    master_profile: Mapped["MasterProfile"] = relationship(back_populates="user", uselist=False)
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
```

*(Остальные схемы в полной версии документа)*

---

## API Endpoints Overview

### User Service

```
POST   /api/v1/auth/telegram         # Authenticate via Telegram
GET    /api/v1/users/me              # Get current user
PATCH  /api/v1/users/me              # Update profile
GET    /api/v1/masters/{master_id}   # Get master profile
PATCH  /api/v1/masters/me            # Update master profile
```

### Practice Service

```
POST   /api/v1/practices                    # Create practice
GET    /api/v1/practices/{practice_id}      # Get practice
PATCH  /api/v1/practices/{practice_id}      # Update practice
DELETE /api/v1/practices/{practice_id}      # Delete practice
POST   /api/v1/practices/{id}/zoom          # Create Zoom meeting
GET    /api/v1/practices                    # List practices (filters)
```

### Quiz Service

```
POST   /api/v1/practices/{id}/quiz          # Create quiz
GET    /api/v1/practices/{id}/quiz          # Get quiz
POST   /api/v1/quizzes/{id}/responses       # Submit response
GET    /api/v1/practices/{id}/quiz/results  # Get aggregated results
```

### Calendar Service

```
GET    /api/v1/calendar/upcoming            # Upcoming practices
GET    /api/v1/calendar/master/{master_id}  # Master calendar
POST   /api/v1/calendar/reminders/{id}      # Manual reminder
```

### Notification Service

```
POST   /api/v1/notifications                # Create notification
GET    /api/v1/notifications/{id}           # Get notification
GET    /api/v1/notifications/user/{user_id} # User notifications
POST   /api/v1/notifications/channel        # Send to channel
POST   /api/v1/notifications/group          # Send to group
```

*(Остальные API endpoints для Booking, Payment, State, Library)*

---

## Next Steps

**Вопрос:** Продолжить детальное описание остальных сервисов (Booking, Payment, State, Library)?

Или сначала хотите обсудить/скорректировать текущую структуру 5 сервисов?

---

**Файл сохранён:** `/mnt/user-data/outputs/master-rooms-architecture-v2.md`
