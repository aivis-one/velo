# VELO — Анализ диаграмм vs ТЗ/ДД

**Дата:** 6 февраля 2026 (обновлено)
**Статус:** Утверждено

---

## 📋 Иерархия истины

```
1. ДизДок (VELO-Design-Document.md)              ← Конституция проекта
2. ТЗ (VELO-Technical-Specification.md)          ← Описание фаз разработки
3. Мокапы (velo-mockups/)                        ← Согласованный UX
4. Payment Meeting                               ← Утвержденная платежная система
5. Data Consistency Semaphores                   ← Проверки целостности данных
──────────────────────────────────────────────────────────────────────────────
6. VELO-Database-Schema.mermaid                  ← ✅ Актуальная схема БД!
7. Старые диаграммы (01-08-*.mermaid)           ← ❌ Устаревшие (микросервисы)
8. tech_spec/ (старые файлы Dec 28)             ← ❌ Legacy, удалить
```

**Правило:** Если mermaid не соответствует ТЗ/ДД → mermaid неправильная.

---

## 🆕 Новые документы

### Data Consistency Semaphores

**Файл:** `VELO-Data-Consistency-Semaphores.md` (6 Feb 2026, 01:38)

**Назначение:** Система автоматических SQL-проверок целостности данных.

**Категории:**
- COUNT = COUNT (1:1 связи) - 4 семафора
- SUM = 0 (Double-Entry) - 2 семафора
- Computed = Actual (кэши) - 5 семафоров
- Orphan Detection - 5 семафоров
- Business Invariants - 5 семафоров

**Статус:** Дополняет ДД раздел 7.4, критически важен для "вайба" кодинга.

**Ключевые проверки frozen/available:**
```sql
-- Semaphore 3.2: frozen_amount = SUM(ledger WHERE frozen=true)
-- Semaphore 3.3: available_amount = SUM(ledger WHERE frozen=false)
-- Semaphore 5.1: Frozen для completed практик = 0
```

---

## 🔍 Найденные расхождения

### 1. ❌ Архитектура (01-architecture-overview.mermaid)

**Что показывает диаграмма:**
```
- API Gateway (Kong/Traefik)
- 9 отдельных микросервисов:
  * User Service
  * Practice Service
  * Quiz Service
  * Calendar Service
  * Notification Service
  * Booking Service
  * Payment Service
  * State Service
  * Library Service
```

**Что в ТЗ (реальность):**
```
MVP = Модульный монолит (один FastAPI сервис)

velo-backend/
├── app/
│   ├── modules/
│   │   ├── auth/           # НЕ отдельный сервис
│   │   ├── users/
│   │   ├── masters/
│   │   ├── practices/
│   │   ├── bookings/
│   │   ├── payments/
│   │   ├── notifications/
│   │   ├── diary/          # НЕТ в старой диаграмме!
│   │   └── admin/          # НЕТ в старой диаграмме!
```

**Вердикт:** ❌ Диаграмма устарела. Нужна новая под модульный монолит.

---

### 2. ✅ Database Schema (VELO-Database-Schema.mermaid)

**ОБНОВЛЕНИЕ:** Обнаружена актуальная версия схемы БД!

**Файл:** `VELO-Database-Schema.mermaid` (6 Feb 2026, 01:38)

**Что в схеме:**
```sql
MASTER_PROFILE {
    uuid user_id PK,FK
    jsonb data "account, availability, profile, settings, stats"
    decimal frozen_amount "computed by listener"       ← ✅ ЕСТЬ!
    decimal available_amount "computed by listener"    ← ✅ ЕСТЬ!
    timestamp created_at
    timestamp updated_at
}

MASTER_LEDGER {
    uuid id PK
    uuid user_id FK
    uuid practice_id FK "nullable, for frozen tracking"
    decimal amount
    boolean is_frozen "true until practice completed"  ← ✅ ЕСТЬ!
    enum status "pending|done|cancelled"
    string reason "sale:practice=456, commission:practice=456"
    text notes
    timestamp created_at
}
```

**Вердикт:** ✅ Схема АКТУАЛЬНА! Полностью соответствует ТЗ и Payment Meeting.

**Старые схемы удалить:**
- `tech_spec/diagrams/03-database-schema.mermaid` (устарела, нет frozen/available)

---

### 3. ❌ Модель платежей (нет диаграммы!)

**Что в Payment Meeting (утверждено):**
```
3 ledger-таблицы (double-entry):
- user_ledger      (баланс юзера)
- master_ledger    (баланс мастера с is_frozen флагом)
- company_ledger   (доход платформы)

Принцип:
- Юзер платит → Мастер получает 100% frozen
- Практика завершена → unfrozen to available
- Мастер платит комиссию 15% из available
```

**Текущие диаграммы:**
- НЕТ диаграммы frozen/available flow
- НЕТ диаграммы ledger-таблиц
- НЕТ диаграммы "комиссия только с живых денег"

**Вердикт:** ❌ Критическая диаграмма отсутствует!

---

### 4. ⚠️ Модули diary и admin

**Что в ТЗ:**
```
app/modules/
├── diary/          # Check-ins, feedbacks, entries
└── admin/          # Верификация, модерация
```

**Текущие диаграммы:**
- НЕТ диаграмм для модуля diary
- НЕТ диаграмм для модуля admin
- Есть только 08-master-verification-flow.mermaid (частично про admin)

**Вердикт:** ⚠️ Недостающие диаграммы.

---

### 5. ❓ State Service / YON State Engine

**Что показывают диаграммы:**
- State Service как отдельный микросервис
- Интеграция с YON State Engine

**Что в ТЗ:**
```
### 1.3. Вне scope MVP
- AI-саммари (только розетка)
```

**Вопрос:** State Service входит в MVP или нет?
**Предположение:** Если diary модуль есть, то check-ins есть. Но интеграция с YON State Engine возможно позже.

**Вердикт:** ❓ Нужно уточнить scope.

---

### 6. ❓ Library Service

**Что показывают диаграммы:**
- Library Service (S3/CDN для записей)

**Что в ТЗ:**
```
### 1.3. Вне scope MVP
- Library (записи практик)
```

**Вердикт:** ❌ Library Service НЕ в MVP. Диаграмма не нужна для MVP.

---

## 📊 Статистика

**Всего mermaid файлов в tech_spec/diagrams/:** 46

**Актуальные файлы:**
- ✅ VELO-Database-Schema.mermaid (6 Feb 2026)
- ✅ VELO-Data-Consistency-Semaphores.md (6 Feb 2026)

**Дубликаты (удалить):**
- 🔄 tech_spec/diagrams/VELO-Design-Document.md (дубликат корневого)
- 🔄 tech_spec/diagrams/VELO-Technical-Specification.md (дубликат корневого)

**Категории:**

| Префикс | Описание | Количество | Статус |
|---------|----------|------------|--------|
| `01-08` | Основные диаграммы | 8 | ❌ Устарели |
| `06b, 06c, 07b-d` | Детализация основных | 6 | ⚠️ Частично устарели |
| `MH-*` | Детальные flow (Calendar, Check-in, etc) | ~31 | ❓ Нужна проверка |

---

## 🎯 Рекомендации

### 1. Удалить дубликаты документов

```bash
# Дубликаты основных документов (в diagrams/)
tech_spec/diagrams/VELO-Design-Document.md           # Дубликат velo/VELO-Design-Document.md
tech_spec/diagrams/VELO-Technical-Specification.md   # Дубликат velo/VELO-Technical-Specification.md
```

### 2. Удалить старую документацию

```bash
# Старая документация (Dec 28)
tech_spec/master-rooms-architecture-v2.md    # Устарела
tech_spec/master-rooms-specification.md      # Устарела
tech_spec/tech_task.md                       # Устарела
tech_spec/index.md                           # Устарел
tech_spec/user-model-jsonb-pattern.md        # Частично устарел (нет frozen/available)
tech_spec/master-profile-jsonb-pattern.md    # Частично устарел (нет frozen/available)
```

### 3. Удалить старые устаревшие диаграммы

```bash
# Все 01-08-*.mermaid и MH-*.mermaid диаграммы (показывают микросервисы, нет frozen/available)
tech_spec/diagrams/01-architecture-overview.mermaid
tech_spec/diagrams/02-api-flow-booking.mermaid
tech_spec/diagrams/03-database-schema.mermaid         # Старая версия БЕЗ frozen/available!
tech_spec/diagrams/04-calendar-reminders.mermaid
tech_spec/diagrams/05-quiz-service.mermaid
tech_spec/diagrams/06-notification-service.mermaid
tech_spec/diagrams/06b-notification-flow-complete.mermaid
tech_spec/diagrams/06c-notification-templates.mermaid
tech_spec/diagrams/07-state-service.mermaid
tech_spec/diagrams/07b-check-in-flow.mermaid
tech_spec/diagrams/07c-feedback-flow.mermaid
tech_spec/diagrams/07d-diary-entry-flow.mermaid
tech_spec/diagrams/08-master-verification-flow.mermaid
tech_spec/diagrams/MH-*.mermaid                       # Все 31+ детальных MH-файлов
```

### 4. Переименовать актуальную схему БД (политика имён)

```bash
# ТЕКУЩЕЕ имя:
VELO-Database-Schema.mermaid

# Политика имён - убрать caps, единообразие:
velo-database-schema.mermaid

# ИЛИ оставить как есть (VELO-* префикс для основных документов)
```

### 5. Создать новые диаграммы (high-level MVP scope)

```bash
# Платежная система (критично!)
diagrams/payment-01-ledger-tables.mermaid
  → Схема 3 ledger-таблиц (user/master/company)

diagrams/payment-02-frozen-available-flow.mermaid
  → User pays → frozen → practice done → unfrozen to available

diagrams/payment-03-commission-flow.mermaid
  → "Комиссия только с живых денег" (15% после практики)

diagrams/payment-04-promo-codes.mermaid
  → Company Promo vs Master Promo (разная экономика)

# Модули
diagrams/module-diary.mermaid
  → Check-ins, feedbacks, diary entries

diagrams/module-admin.mermaid
  → Верификация мастеров, модерация
```

### Проверить и оставить/обновить

```bash
diagrams/04-calendar-reminders.mermaid
  → Проверить актуальность (24h/1h/10min reminders)

diagrams/06-notification-service.mermaid
  → Проверить актуальность (Telegram bot)

diagrams/08-master-verification-flow.mermaid
  → Актуальна (pending → verified)

diagrams/MH-* (31 файл)
  → Детальная проверка каждого (может быть актуально)
```

### Удалить (вне scope MVP)

```bash
diagrams/*library*.mermaid           # Library вне MVP
diagrams/*state*.mermaid (частично)  # Если State Service вне MVP
diagrams/*zoom*.mermaid (если есть)  # Zoom интеграция скрыта в practices module
```

---

## 📝 Финальный план cleanup

### ✅ Утверждённый план (Вариант А + однообразие имён)

**Шаг 1: Удалить**
```bash
# Дубликаты документов
rm tech_spec/diagrams/VELO-Design-Document.md
rm tech_spec/diagrams/VELO-Technical-Specification.md

# Старая документация
rm tech_spec/master-rooms-architecture-v2.md
rm tech_spec/master-rooms-specification.md
rm tech_spec/tech_task.md
rm tech_spec/index.md
rm tech_spec/user-model-jsonb-pattern.md
rm tech_spec/master-profile-jsonb-pattern.md

# Все старые диаграммы (показывают микросервисы, устарели)
rm tech_spec/diagrams/*.mermaid      # Все 46 файлов

# Удалить README.md в корне (устарел, ссылается на YON)
rm README.md
```

**Шаг 2: Переместить актуальную схему БД**
```bash
# Переместить актуальную схему из diagrams/ в корень velo/
mv tech_spec/diagrams/VELO-Database-Schema.mermaid ./VELO-Database-Schema.mermaid

# Теперь все VELO-* документы в корне:
# - VELO-Design-Document.md
# - VELO-Technical-Specification.md
# - VELO-Payment-System-Meeting.md
# - VELO-Data-Consistency-Semaphores.md
# - VELO-Database-Schema.mermaid
```

**Шаг 3: Удалить пустые папки**
```bash
# После удаления всех .mermaid файлов:
rmdir tech_spec/diagrams/     # Будет пустая
rmdir tech_spec/              # Если пустая после cleanup
```

**Шаг 4: Создать новые диаграммы (в будущем, после cleanup)**
```bash
mkdir -p diagrams/

# Создать 9 high-level диаграмм для MVP:
diagrams/
├── velo-01-modular-monolith.mermaid       # Архитектура модульного монолита
├── velo-02-booking-flow.mermaid           # User journey: запись на практику
├── velo-03-payment-ledgers.mermaid        # 3 ledger tables схема
├── velo-04-frozen-available-flow.mermaid  # Frozen → Available механизм
├── velo-05-commission-flow.mermaid        # 15% комиссия после практики
├── velo-06-promo-codes.mermaid            # Company vs Master promo
├── velo-07-master-verification.mermaid    # Верификация мастеров
├── velo-08-diary-module.mermaid           # Check-ins/Feedback
└── velo-09-waitlist-flow.mermaid          # Очередь ожидания

# Политика имён: velo-NN-название.mermaid (lowercase, дефисы)
```

---

## ✅ Уточнённые вопросы (RESOLVED)

1. **State Service в MVP?** → ✅ Локальное хранение check-in данных (diary module)
2. **Quiz Service в MVP?** → ✅ Отдельная сущность, актуально для MVP
3. **Zoom integration?** → ✅ Достаточно упоминания в practices module (zoom_link поле)
4. **Детальность диаграмм?** → ✅ Вариант А1 - только high-level (9 диаграмм)

---

## 🎯 Файловая структура ПОСЛЕ cleanup

```
velo/
├── VELO-Design-Document.md                    ← Конституция
├── VELO-Technical-Specification.md            ← ТЗ с фазами
├── VELO-Payment-System-Meeting.md             ← Платёжная система
├── VELO-Data-Consistency-Semaphores.md        ← Проверки целостности
├── VELO-Database-Schema.mermaid               ← Актуальная схема БД
├── CLEANUP-REPORT.md                          ← Старый отчёт (обновить или удалить)
├── DIAGRAMS-ANALYSIS.md                       ← Этот файл (обновлён)
├── velo-mockups/                              ← UX мокапы
│   ├── user.html
│   ├── master.html
│   └── admin.html
├── CORE/                                      ← Проектная база знаний
│   ├── core.yaml
│   ├── team.yaml
│   ├── product.yaml
│   ├── tech.yaml
│   ├── ...
│   └── README.md
└── diagrams/                                  ← (создать позже)
    ├── velo-01-modular-monolith.mermaid
    ├── velo-02-booking-flow.mermaid
    └── ... (9 диаграмм)
```

**Удалено:**
- ❌ tech_spec/ (вся папка)
- ❌ README.md (устарел, ссылается на YON)

---

## 🎬 Статус

**Prepared by:** Claude
**Status:** ✅ Утверждено
**Next:** Ждём команды **"Делаем"** для выполнения cleanup
