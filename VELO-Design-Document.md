# VELO — Дизайн-документ (Конституция)

**Версия:** 1.0  
**Дата:** 5 февраля 2026  
**Статус:** Draft

---

## 1. Введение

### 1.1. Миссия продукта

> **Мастера хотят творить, а не быть бухгалтерами и секретарями.**
> 
> VELO снимает рутину по максимуму.

VELO — платформа для мастеров медитаций, йоги, breathwork и других практик. Она автоматизирует:
- Записи на практики
- Очереди ожидания
- Напоминания участникам
- Сбор оплаты
- Учёт посещаемости
- Сбор обратной связи
- Аналитику

### 1.2. Целевая аудитория

| Роль | Описание |
|------|----------|
| **User (Участник)** | Человек, который посещает практики |
| **Master (Мастер)** | Ведущий практик. Может быть одновременно участником чужих практик |
| **Admin** | Администратор платформы. Верификация мастеров, модерация, поддержка |

### 1.3. Глоссарий

| Термин | Определение |
|--------|-------------|
| **Практика** | Сессия (медитация, йога, breathwork и т.д.), проводимая мастером |
| **Бронирование** | Резервация места на практике участником |
| **Check-in** | Фиксация состояния участника ДО практики |
| **Feedback** | Обратная связь участника ПОСЛЕ практики |
| **Ledger** | Журнал финансовых транзакций (принцип double-entry) |
| **Waitlist** | Очередь ожидания на заполненную практику |

---

## 2. Принципы продукта

### 2.1. Мастера хотят творить, а не быть бухгалтерами

Каждая функция VELO должна отвечать на вопрос: **"Это снимает рутину с мастера?"**

| Рутина | Было (вручную) | Стало (VELO) |
|--------|----------------|--------------|
| Записи на практику | Сообщения "запишите меня" | Автоматические брони |
| Очередь ожидания | "Напишу если место освободится" | Waitlist + авто-уведомления |
| Напоминания | "Не забудьте, завтра в 10:00" | Авто (24ч, 1ч, 10мин) |
| Сбор оплаты | "Переведите на карту" | Stripe, автоматически |
| Учёт посещений | Галочки в блокноте | Attendance tracking |
| Обратная связь | "Напишите как вам" | Check-in / Feedback формы |

### 2.2. Бесшовная миграция

Мастера уже работают в Telegram. VELO не должен ломать их привычки:

- Поддерживаем те же типы практик (live, series, one_on_one, replay)
- Telegram WebApp — привычная среда
- Постепенное добавление функций, не шоковая терапия

### 2.3. Архитектура готова к масштабированию

Модульный монолит сейчас → микросервисы потом:

- Каждый модуль изолирован
- БД спроектирована под будущий распил
- JSONB для неустоявшихся структур (credentials, master_profile)
- Отдельные таблицы для разных доменов

---

## 3. Технологический стек

### 3.1. Backend

| Компонент | Технология | Версия |
|-----------|------------|--------|
| Язык | Python | 3.12 |
| Фреймворк | FastAPI | latest |
| ORM | SQLAlchemy | 2.0 (async) |
| Валидация | Pydantic | v2 |
| Тестирование | pytest, pytest-asyncio | latest |

### 3.2. Database

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Primary DB | PostgreSQL 16 | Все данные |
| Cache/Sessions | Redis 7 | Сессии, очереди, кэш |

### 3.3. External Services

| Сервис | Назначение |
|--------|------------|
| Stripe | Платежи (пополнение, выводы) |
| Telegram Bot API | Уведомления |
| Telegram WebApp | Фронтенд (MVP) |

### 3.4. Infrastructure

| Компонент | Технология |
|-----------|------------|
| Контейнеризация | Docker + Docker Compose |
| Хостинг | VPS |
| CI/CD | GitHub Actions |

---

## 4. Архитектура

### 4.1. Модульный монолит → Микросервисы

**MVP:** Один сервис, разбитый на модули.

**Будущее:** Каждый модуль может стать отдельным микросервисом.

```
velo-backend/
├── app/
│   ├── modules/
│   │   ├── auth/           # Telegram auth, сессии
│   │   ├── users/          # Профили, роли
│   │   ├── masters/        # Профили мастеров
│   │   ├── practices/      # CRUD практик
│   │   ├── bookings/       # Бронирования, waitlist
│   │   ├── payments/       # Ledgers, Stripe
│   │   ├── notifications/  # Telegram-бот, напоминания
│   │   ├── diary/          # Check-ins, feedbacks, entries
│   │   └── admin/          # Верификация, модерация
│   ├── core/               # DB, Redis, config, middlewares
│   └── api/                # FastAPI routers
├── tests/
└── docker-compose.yml
```

### 4.2. Структура модуля

Каждый модуль содержит:

```
module/
├── models.py       # SQLAlchemy models
├── schemas.py      # Pydantic schemas
├── service.py      # Business logic
├── router.py       # FastAPI endpoints
└── exceptions.py   # Module-specific exceptions
```

### 4.3. Схема БД

#### Core
| Таблица | Назначение | Особенности |
|---------|------------|-------------|
| `users` | Все пользователи | `credentials: JSONB` |
| `master_profiles` | Профили мастеров | `data: JSONB`, `frozen_amount`, `available_amount` |

#### Practices
| Таблица | Назначение | Особенности |
|---------|------------|-------------|
| `practices` | Практики | type: live, series, one_on_one, replay |
| `practice_pricing` | Цены практик | Отдельно для Payment Service |

#### Bookings
| Таблица | Назначение |
|---------|------------|
| `bookings` | Бронирования |
| `waitlist` | Очередь ожидания |

#### Payments (Double-Entry Ledgers)
| Таблица | Назначение |
|---------|------------|
| `user_ledger` | Баланс юзеров |
| `master_ledger` | Баланс мастеров (с `is_frozen`) |
| `company_ledger` | Revenue компании |
| `payments` | Внешние операции (Stripe) |
| `purchases` | История покупок |
| `promos` | Промокоды (Company + Master) |

#### State (Diary)
| Таблица | Назначение |
|---------|------------|
| `checkins` | Состояние ДО практики |
| `feedbacks` | Обратная связь ПОСЛЕ практики |
| `diary_entries` | Личные записи юзера |

#### Notifications
| Таблица | Назначение |
|---------|------------|
| `notifications` | Уведомления |
| `notification_deliveries` | Статус доставки |

### 4.4. Будущий распил на микросервисы

```
User Service:
  ├── users
  ├── user_auths (из credentials JSONB)
  └── diary_entries

Master Service:
  └── master_profiles

Practice Service:
  └── practices

Booking Service:
  ├── bookings
  └── waitlist

Payment Service:
  ├── practice_pricing
  ├── user_ledger
  ├── master_ledger
  ├── company_ledger
  ├── payments
  └── purchases

State Service:
  ├── checkins
  └── feedbacks

Notification Service:
  ├── notifications
  └── notification_deliveries
```

---

## 5. Роли и права доступа

### 5.1. User (Участник)

**Может:**
- Просматривать практики
- Бронировать / отменять брони
- Пополнять баланс
- Покупать практики
- Заполнять check-in / feedback
- Вести дневник
- Редактировать свой профиль
- Подавать заявку на мастера

**Не может:**
- Создавать практики
- Видеть данные других юзеров
- Выводить деньги (только тратить)

### 5.2. Master (Мастер)

**Всё что User, плюс:**
- Создавать / редактировать / удалять свои практики
- Видеть список участников своих практик
- Видеть агрегированные check-ins / feedbacks своих практик
- Видеть свою аналитику (статистика, заработок)
- Выводить деньги с master_balance
- Переводить деньги с master_balance на user_balance

**Не может:**
- Видеть данные чужих практик
- Верифицировать других мастеров

### 5.3. Admin

**Всё что Master, плюс:**
- Видеть всех юзеров и мастеров
- Верифицировать / блокировать мастеров
- Модерировать жалобы
- Подтверждать выводы средств
- Видеть финансовую аналитику платформы
- Отправлять broadcast-уведомления

---

## 6. Платежи и балансы

### 6.1. Принцип Double-Entry

> **Золотое правило:** Сумма всех дебетов = Сумма всех кредитов
>
> Если где-то что-то записалось, значит где-то что-то списалось.
> Сумма всех операций в системе ВСЕГДА = 0.

Каждая операция — минимум 2 записи в разных журналах.

### 6.2. Три журнала

| Журнал | Владелец | Назначение |
|--------|----------|------------|
| `user_ledger` | User | Кошелёк юзера (пополнения, покупки) |
| `master_ledger` | Master | Заработок мастера (frozen + available) |
| `company_ledger` | Platform | Доход компании (комиссии, маркетинг) |

### 6.3. Master Balance: Frozen vs Available

> **Master Balance — это ЗАРАБОТОК. User Balance — это КОШЕЛЁК. Никогда не смешиваем.**

| | Frozen | Available |
|--|--------|-----------|
| **Когда появляется** | Юзер оплатил практику | Практика успешно завершена |
| **Можно вывести** | ❌ Нет | ✅ Да |
| **Можно перевести на User Balance** | ❌ Нет | ✅ Да |
| **При отмене практики** | Возвращается юзеру | — |

В `MasterProfile` хранятся два поля для быстрого доступа:
- `frozen_amount` — заморожено (ожидает практик)
- `available_amount` — доступно для вывода

Обновляются listeners при записи в `master_ledger`.

### 6.4. Потоки денег

#### Пополнение баланса (Stripe → User)
```
payments:     direction=in, amount=+100, status=confirmed
user_ledger:  user_id=1, amount=+100, reason="payment:123"
──────────────────────────────────────────────────
Σ = 0 ✓ (деньги вошли в систему извне)
```

#### Покупка практики ($50) — Шаг 1: Регистрация
> Юзер платит Мастеру 100%. Деньги замораживаются.
```
user_ledger:   user_id=1, amount=-50, reason="purchase:practice=456"
master_ledger: user_id=2, amount=+50, is_frozen=true, reason="sale:practice=456"
purchases:     user_id=1, practice_id=456, amount=50, status=pending
──────────────────────────────────────────────────
Master Profile: frozen_amount += 50
Σ = -50 + 50 = 0 ✓
```

#### Покупка практики ($50) — Шаг 2: Практика завершена
> Разморозка + списание комиссии 15%.
```
master_ledger: user_id=2, UPDATE is_frozen=false WHERE practice=456
master_ledger: user_id=2, amount=-7.50, reason="commission:practice=456"
company_ledger: amount=+7.50, type=commission, reason="commission:practice=456"
purchases:     UPDATE status=completed
──────────────────────────────────────────────────
Master Profile: frozen=0, available=42.50
Σ = -7.50 + 7.50 = 0 ✓
```

#### Бесплатная практика (price = $0)
> Комиссия = 15% от живых денег. Нет денег = нет комиссии.
```
user_ledger:   user_id=1, amount=0, reason="purchase:practice=789"
master_ledger: user_id=2, amount=0, is_frozen=true, reason="sale:practice=789"
──────────────────────────────────────────────────
После завершения: company_ledger записи НЕТ (комиссия $0)
Σ = 0 ✓
```
**Зачем нулевые записи:** консистентность отчётности. `COUNT(purchases)` = все участники.

#### Перевод Master → User (для покупки чужой практики)
> Только из Available. Frozen переводить нельзя.
```
master_ledger: user_id=2, amount=-50, reason="transfer:internal"
user_ledger:   user_id=2, amount=+50, reason="transfer:internal"
──────────────────────────────────────────────────
Master Profile: available_amount -= 50
Σ = -50 + 50 = 0 ✓
```

#### Вывод мастером
> Только из Available. Минимальная сумма и комиссия — настраиваемые.
```
master_ledger:  user_id=2, amount=-1000, reason="withdrawal:payment=789"
company_ledger: amount=+2, type=withdrawal_fee, reason="withdrawal:payment=789"
payments:       direction=out, user_id=2, amount=998, status=pending
──────────────────────────────────────────────────
Master Profile: available_amount -= 1000
Σ = 0 ✓ (деньги покидают систему)
```
**Важно:** выводы подтверждает админ вручную. Автоматических выплат нет.

### 6.5. Отмены и возвраты

#### Юзер отменяет бронирование
| Условие | Результат |
|---------|-----------|
| > 24ч до практики | 100% возврат |
| < 24ч до практики | 0% возврат (деньги остаются frozen) |

```
# Отмена > 24ч:
master_ledger: user_id=2, amount=-50, reason="refund:practice=456"
user_ledger:   user_id=1, amount=+50, reason="refund:practice=456"
──────────────────────────────────────────────────
Master Profile: frozen_amount -= 50
Σ = +50 - 50 = 0 ✓
```

#### Мастер отменяет практику
> Автоматический 100% возврат всем участникам.
```
# Для каждого участника:
master_ledger: user_id=2, amount=-50, reason="refund:practice=456,cancelled_by_master"
user_ledger:   user_id=N, amount=+50, reason="refund:practice=456"
```

#### No-show (юзер не пришёл)
> Деньги остаются у мастера. Стандартный flow завершения практики.

### 6.6. Промокоды

#### Company Promo (компания платит за маркетинг)
> Мастер получает деньги из маркетингового бюджета компании.
```
# Промокод WELCOME (100% скидка), практика $50:
user_ledger:    user_id=1, amount=0, reason="purchase:practice=456,promo:WELCOME"
master_ledger:  user_id=2, amount=+50, is_frozen=true, reason="sale:practice=456"
company_ledger: amount=-50, type=marketing, reason="promo:WELCOME,practice=456"
──────────────────────────────────────────────────
После практики: комиссия $0 (юзер заплатил $0 живых денег)
Σ = 0 ✓
```

#### Master Promo (мастер отказывается от выручки)
> Промокод создаёт сам мастер. Компания ничего не платит.
```
# Промокод ALEX-VIP (100% скидка), практика $50:
user_ledger:   user_id=1, amount=0, reason="purchase:practice=456,promo:ALEX-VIP"
master_ledger: user_id=2, amount=0, is_frozen=true, reason="sale:practice=456,promo:ALEX-VIP"
──────────────────────────────────────────────────
Мастер решил не брать деньги. Company ledger не затронут.
Σ = 0 ✓
```

### 6.7. Настраиваемые переменные

| Переменная | Описание | Значение |
|------------|----------|----------|
| `PLATFORM_COMMISSION_PERCENT` | Комиссия платформы | 15% |
| `MIN_WITHDRAWAL_AMOUNT` | Минимум для вывода | $50 |
| `WITHDRAWAL_FEE` | Комиссия за вывод | $2 |
| `CANCELLATION_DEADLINE_HOURS` | Дедлайн отмены с возвратом | 24ч |
| `MASTER_PROMO_DISCOUNTS` | Доступные скидки | [5, 25, 50, 75, 100] |

---

## 7. Правила разработки

### 7.1. Что можно

- Использовать только ORM (SQLAlchemy)
- Комментарии к коду — на английском
- Общение — на русском
- JSONB для неустоявшихся структур
- Type hints везде
- Async/await для I/O операций

### 7.2. Что нельзя

| Запрещено | Почему |
|-----------|--------|
| Raw SQL | Только ORM |
| Прямое изменение балансов | Только через ledger + listener |
| Синхронные I/O операции | Блокируют event loop |
| Хардкод конфигов | Только env variables |
| Бизнес-логика в роутерах | Только в service layer |

### 7.3. Код-стайл

- **Formatter:** black
- **Linter:** ruff
- **Type checker:** mypy (strict mode)
- **Naming:** snake_case для функций/переменных, PascalCase для классов
- **Docstrings:** Google style

### 7.4. Консистентность данных

> **Принцип:** Данные должны быть проверяемыми. Если что-то можно посчитать двумя способами — оба способа должны давать одинаковый результат.

#### Data Consistency Semaphores

Семафоры — это простые SQL-проверки, которые должны возвращать ожидаемый результат. Расхождение = алерт.

**Категории проверок:**

| Категория | Пример | Ожидание |
|-----------|--------|----------|
| COUNT = COUNT | bookings vs purchases | Равны |
| SUM = 0 | Σ всех ledgers | = 0 (double-entry) |
| Computed = Actual | User.balance_user vs SUM(ledger) | Равны |
| Orphan Detection | Booking без Practice | 0 записей |
| Invariants | Отрицательный баланс | 0 записей |

**Правило для разработки:**

При добавлении новой таблицы или связи:
1. **1:1 связь?** → Добавь COUNT = COUNT семафор
2. **Кэшированное поле?** → Добавь Computed = Actual семафор
3. **FK на другую таблицу?** → Добавь Orphan Detection
4. **Бизнес-правило?** → Добавь Invariant семафор

**Полная документация:** `VELO-Data-Consistency-Semaphores.md`

---

## 8. Розетки для будущего

### 8.1. AI-саммари

**Статус:** Розетка (внешний сервис)

**Интерфейс:**
```python
class AIService(Protocol):
    async def generate_summary(
        self,
        practice_id: UUID,
        checkins: list[Checkin],
        feedbacks: list[Feedback]
    ) -> str:
        """Generate AI summary for master."""
        ...
```

**MVP:** Mock-реализация или заглушка.

### 8.2. Library (Записи практик)

**Статус:** TODO

**Таблицы (будущие):**
- `recordings` — метаданные записей
- S3 для хранения файлов

### 8.3. Подписки

**Статус:** Розетка в payments

**Таблица:**
```python
class Subscription:
    id: UUID
    user_id: UUID
    plan: Enum  # monthly, yearly
    status: Enum  # active, cancelled, expired
    stripe_subscription_id: str
    current_period_start: datetime
    current_period_end: datetime
```

**MVP:** Таблица создана, логика не реализована.

### 8.4. OAuth (Google, Apple)

**Статус:** Розетка в credentials JSONB

**MVP:** Только Telegram auth.

**Будущее:**
```json
{
  "telegram": {"id": 123456789},
  "google": {"id": "...", "email": "..."},
  "apple": {"id": "..."}
}
```

Затем миграция в отдельную таблицу `user_auths`.

---

## 9. Мокапы и UI

### 9.1. User App

**Tab Bar:**
- 🏠 Дашборд
- 📅 Календарь
- 📔 Дневник
- 👤 Профиль

**Основные flow:**
1. Auth: Welcome → Login → Onboarding → Dashboard
2. Practice: Calendar → Detail → Book → Check-in → Live → Feedback
3. Diary: Tabs (All / Check-ins / Feedbacks / Entries)

### 9.2. Master App

**Tab Bar:**
- 📊 Дашборд
- 📅 Практики
- 📈 Аналитика
- 👤 Профиль

**Основные flow:**
1. Auth: Landing → Заявка (3 шага) → Pending → Onboarding
2. Dashboard: AI-саммари, статистика, ученики
3. Practices: Upcoming/Past, создание, редактирование

### 9.3. Admin Panel

**Bottom Nav:**
- 📊 Дашборд
- 👥 Мастера
- ⚠️ Модерация

**Основные flow:**
1. Dashboard: Алерты, метрики
2. Masters: Верификация (pending → verified)
3. Moderation: Обращения, жалобы

---

## Приложения

### A. Ссылки на мокапы

- `velo-mockups/user.html` — User App
- `velo-mockups/master.html` — Master App
- `velo-mockups/admin.html` — Admin Panel

### B. Готовые компоненты для переиспользования

- `notification.py` — модель уведомлений
- `notification_processor.py` — фоновый воркер
- `message_manager.py` — отправка через aiogram
- `templates.py` — шаблоны сообщений
- `user_decorator.py` — middleware для инъекции user
- `balance_listeners.py` — пересчёт балансов

---

**Конец документа**
