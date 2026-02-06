# VELO — Data Consistency Semaphores

**Версия:** 1.0  
**Дата:** 6 февраля 2026  
**Статус:** Draft

---

## 1. Концепция

**Data Consistency Semaphores** — это набор простых SQL-проверок, которые должны возвращать ожидаемый результат. Если результат отличается — данные разошлись, нужен алерт.

### Принципы

| # | Принцип |
|---|---------|
| 1 | **Легковесность** — только COUNT, SUM, простые JOIN-ы |
| 2 | **Независимость** — чистый SQL, не зависит от приложения |
| 3 | **Автономность** — работает даже после распила на микросервисы |
| 4 | **Алертинг** — расхождение → сигнал в Slack/Telegram |

### Архитектура (будущее)

```
┌─────────────────────────────────────────────────────────────┐
│                    Semaphore Service                        │
│              (cron job, каждые 1-10 минут)                  │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ User DB  │  │ Payment  │  │ Booking  │  │ Practice │
   │          │  │ DB       │  │ DB       │  │ DB       │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │  Alert: Telegram /  │
                    │  Slack / PagerDuty  │
                    └─────────────────────┘
```

---

## 2. Категории семафоров

### 2.1. COUNT = COUNT (1:1 связи)

Проверка: количество записей в связанных таблицах должно совпадать.

| Таблица A | Таблица B | Условие | Ожидание |
|-----------|-----------|---------|----------|
| `bookings` | `purchases` | status != 'cancelled' | A = B |
| `bookings` | `purchases` | status = 'cancelled' | A = B |
| `users` (role='master') | `master_profiles` | — | A = B |
| `practices` | `practice_pricing` | — | A = B |

---

### 2.2. SUM = 0 (Double-Entry Accounting)

Проверка: сумма всех записей в ledger-ах должна равняться нулю.

| Проверка | Ожидание |
|----------|----------|
| Σ (user_ledger + master_ledger + company_ledger) | = 0 |
| Σ по каждой завершённой практике | = 0 |

---

### 2.3. Computed = Actual (кэшированные значения)

Проверка: кэшированные поля соответствуют источнику правды.

| Кэш | Источник правды | Ожидание |
|-----|-----------------|----------|
| `User.balance_user` | SUM(user_ledger) | = |
| `MasterProfile.frozen_amount` | SUM(master_ledger WHERE frozen) | = |
| `MasterProfile.available_amount` | SUM(master_ledger WHERE !frozen) | = |
| `Practice.current_participants` | COUNT(active bookings) | = |
| `Promo.used_count` | COUNT(purchases with promo) | = |

---

### 2.4. Orphan Detection (сироты)

Проверка: нет записей, ссылающихся на несуществующие сущности.

| Проверка | Ожидание |
|----------|----------|
| Booking без Practice | 0 |
| Booking без User | 0 |
| Purchase без User | 0 |
| MasterLedger без User | 0 |
| NotificationDelivery без Notification | 0 |

---

### 2.5. Business Logic Invariants

Проверка: бизнес-правила не нарушены.

| Проверка | Ожидание |
|----------|----------|
| Frozen ledger для completed практик | 0 |
| Отрицательный available_amount | 0 |
| Attended до начала практики | 0 |

---

## 3. SQL-запросы

### 3.1. COUNT = COUNT

```sql
-- Semaphore 1.1: Bookings = Purchases (active)
SELECT 
    (SELECT COUNT(*) FROM bookings WHERE status != 'cancelled') as bookings,
    (SELECT COUNT(*) FROM purchases WHERE status != 'cancelled') as purchases,
    CASE WHEN 
        (SELECT COUNT(*) FROM bookings WHERE status != 'cancelled') = 
        (SELECT COUNT(*) FROM purchases WHERE status != 'cancelled')
    THEN 'OK' ELSE 'ALERT' END as status;

-- Semaphore 1.2: Bookings = Purchases (cancelled)
SELECT 
    (SELECT COUNT(*) FROM bookings WHERE status = 'cancelled') as bookings,
    (SELECT COUNT(*) FROM purchases WHERE status = 'cancelled') as purchases,
    CASE WHEN 
        (SELECT COUNT(*) FROM bookings WHERE status = 'cancelled') = 
        (SELECT COUNT(*) FROM purchases WHERE status = 'cancelled')
    THEN 'OK' ELSE 'ALERT' END as status;

-- Semaphore 1.3: Masters = MasterProfiles
SELECT 
    (SELECT COUNT(*) FROM users WHERE role = 'master') as masters,
    (SELECT COUNT(*) FROM master_profiles) as profiles,
    CASE WHEN 
        (SELECT COUNT(*) FROM users WHERE role = 'master') = 
        (SELECT COUNT(*) FROM master_profiles)
    THEN 'OK' ELSE 'ALERT' END as status;

-- Semaphore 1.4: Practices = PracticePricing
SELECT 
    (SELECT COUNT(*) FROM practices) as practices,
    (SELECT COUNT(*) FROM practice_pricing) as pricing,
    CASE WHEN 
        (SELECT COUNT(*) FROM practices) = 
        (SELECT COUNT(*) FROM practice_pricing)
    THEN 'OK' ELSE 'ALERT' END as status;
```

---

### 3.2. SUM = 0

```sql
-- Semaphore 2.1: Global double-entry balance
SELECT 
    (SELECT COALESCE(SUM(amount), 0) FROM user_ledger WHERE status = 'done') as user_sum,
    (SELECT COALESCE(SUM(amount), 0) FROM master_ledger WHERE status = 'done') as master_sum,
    (SELECT COALESCE(SUM(amount), 0) FROM company_ledger WHERE status = 'done') as company_sum,
    (
        (SELECT COALESCE(SUM(amount), 0) FROM user_ledger WHERE status = 'done') +
        (SELECT COALESCE(SUM(amount), 0) FROM master_ledger WHERE status = 'done') +
        (SELECT COALESCE(SUM(amount), 0) FROM company_ledger WHERE status = 'done')
    ) as total,
    CASE WHEN (
        (SELECT COALESCE(SUM(amount), 0) FROM user_ledger WHERE status = 'done') +
        (SELECT COALESCE(SUM(amount), 0) FROM master_ledger WHERE status = 'done') +
        (SELECT COALESCE(SUM(amount), 0) FROM company_ledger WHERE status = 'done')
    ) = 0 THEN 'OK' ELSE 'ALERT' END as status;

-- Semaphore 2.2: Per-practice balance (completed only)
-- Returns rows only if there are problems
SELECT 
    p.id as practice_id,
    p.title,
    COALESCE(SUM(ul.amount), 0) as user_sum,
    COALESCE(SUM(ml.amount), 0) as master_sum,
    COALESCE(SUM(ul.amount), 0) + COALESCE(SUM(ml.amount), 0) as balance
FROM practices p
LEFT JOIN purchases pu ON pu.practice_id = p.id
LEFT JOIN user_ledger ul ON ul.reason LIKE '%practice=' || p.id::text || '%'
LEFT JOIN master_ledger ml ON ml.practice_id = p.id
WHERE p.status = 'completed'
GROUP BY p.id, p.title
HAVING COALESCE(SUM(ul.amount), 0) + COALESCE(SUM(ml.amount), 0) != 0;
-- Expected: 0 rows
```

---

### 3.3. Computed = Actual

```sql
-- Semaphore 3.1: User balances match ledger
-- Returns rows only if there are mismatches
SELECT 
    u.id,
    u.first_name,
    u.balance_user as cached,
    COALESCE(SUM(ul.amount), 0) as actual,
    u.balance_user - COALESCE(SUM(ul.amount), 0) as diff
FROM users u
LEFT JOIN user_ledger ul ON ul.user_id = u.id AND ul.status = 'done'
GROUP BY u.id, u.first_name, u.balance_user
HAVING u.balance_user != COALESCE(SUM(ul.amount), 0);
-- Expected: 0 rows

-- Semaphore 3.2: Master frozen amounts match ledger
SELECT 
    mp.user_id,
    u.first_name,
    mp.frozen_amount as cached,
    COALESCE(SUM(ml.amount), 0) as actual,
    mp.frozen_amount - COALESCE(SUM(ml.amount), 0) as diff
FROM master_profiles mp
JOIN users u ON u.id = mp.user_id
LEFT JOIN master_ledger ml ON ml.user_id = mp.user_id 
    AND ml.is_frozen = true 
    AND ml.status = 'done'
GROUP BY mp.user_id, u.first_name, mp.frozen_amount
HAVING mp.frozen_amount != COALESCE(SUM(ml.amount), 0);
-- Expected: 0 rows

-- Semaphore 3.3: Master available amounts match ledger
SELECT 
    mp.user_id,
    u.first_name,
    mp.available_amount as cached,
    COALESCE(SUM(ml.amount), 0) as actual,
    mp.available_amount - COALESCE(SUM(ml.amount), 0) as diff
FROM master_profiles mp
JOIN users u ON u.id = mp.user_id
LEFT JOIN master_ledger ml ON ml.user_id = mp.user_id 
    AND ml.is_frozen = false 
    AND ml.status = 'done'
GROUP BY mp.user_id, u.first_name, mp.available_amount
HAVING mp.available_amount != COALESCE(SUM(ml.amount), 0);
-- Expected: 0 rows

-- Semaphore 3.4: Practice participant count
SELECT 
    p.id,
    p.title,
    p.current_participants as cached,
    COUNT(b.id) as actual,
    p.current_participants - COUNT(b.id) as diff
FROM practices p
LEFT JOIN bookings b ON b.practice_id = p.id 
    AND b.status IN ('confirmed', 'attended')
GROUP BY p.id, p.title, p.current_participants
HAVING p.current_participants != COUNT(b.id);
-- Expected: 0 rows

-- Semaphore 3.5: Promo used_count
SELECT 
    pr.id,
    pr.code,
    pr.used_count as cached,
    COUNT(pu.id) as actual,
    pr.used_count - COUNT(pu.id) as diff
FROM promos pr
LEFT JOIN purchases pu ON pu.promo_id = pr.id 
    AND pu.status != 'cancelled'
GROUP BY pr.id, pr.code, pr.used_count
HAVING pr.used_count != COUNT(pu.id);
-- Expected: 0 rows
```

---

### 3.4. Orphan Detection

```sql
-- Semaphore 4.1: Orphan bookings (no practice)
SELECT 
    COUNT(*) as orphan_count,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM bookings b
WHERE NOT EXISTS (SELECT 1 FROM practices p WHERE p.id = b.practice_id);

-- Semaphore 4.2: Orphan bookings (no user)
SELECT 
    COUNT(*) as orphan_count,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM bookings b
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = b.user_id);

-- Semaphore 4.3: Orphan purchases (no user)
SELECT 
    COUNT(*) as orphan_count,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM purchases pu
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = pu.user_id);

-- Semaphore 4.4: Orphan master_ledger (no user)
SELECT 
    COUNT(*) as orphan_count,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM master_ledger ml
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = ml.user_id);

-- Semaphore 4.5: Orphan notification_deliveries (no notification)
SELECT 
    COUNT(*) as orphan_count,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM notification_deliveries nd
WHERE NOT EXISTS (SELECT 1 FROM notifications n WHERE n.id = nd.notification_id);
```

---

### 3.5. Business Logic Invariants

```sql
-- Semaphore 5.1: Frozen money for completed practices (should be 0)
SELECT 
    COUNT(*) as frozen_completed,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM master_ledger ml
JOIN practices p ON p.id = ml.practice_id
WHERE ml.is_frozen = true 
    AND ml.status = 'done'
    AND p.status = 'completed';

-- Semaphore 5.2: Negative available balance (should be 0)
SELECT 
    COUNT(*) as negative_count,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM master_profiles
WHERE available_amount < 0;

-- Semaphore 5.3: Negative user balance (should be 0)
SELECT 
    COUNT(*) as negative_count,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM users
WHERE balance_user < 0;

-- Semaphore 5.4: Attended before practice started (should be 0)
SELECT 
    COUNT(*) as early_attendance,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM bookings b
JOIN practices p ON p.id = b.practice_id
WHERE b.status = 'attended' 
    AND b.joined_at < p.scheduled_at;

-- Semaphore 5.5: More participants than max_participants
SELECT 
    p.id,
    p.title,
    p.max_participants,
    p.current_participants,
    CASE WHEN p.current_participants <= p.max_participants 
    THEN 'OK' ELSE 'ALERT' END as status
FROM practices p
WHERE p.max_participants IS NOT NULL
    AND p.current_participants > p.max_participants;
-- Expected: 0 rows

-- Semaphore 5.6: Financial events without audit log
-- Every purchase should have corresponding audit_log entry
SELECT 
    COUNT(*) as missing_audit,
    CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'ALERT' END as status
FROM purchases pu
WHERE pu.status = 'completed'
    AND NOT EXISTS (
        SELECT 1 FROM audit_logs al 
        WHERE al.event = 'purchase_created' 
        AND al.target_id = pu.id
    );
-- Expected: 0
```

---

## 4. Сводная таблица

| # | Категория | Семафор | Частота | Критичность |
|---|-----------|---------|---------|-------------|
| 1.1 | COUNT=COUNT | Bookings = Purchases (active) | 1 min | 🔴 Critical |
| 1.2 | COUNT=COUNT | Bookings = Purchases (cancelled) | 1 min | 🔴 Critical |
| 1.3 | COUNT=COUNT | Masters = MasterProfiles | 5 min | 🟡 Warning |
| 1.4 | COUNT=COUNT | Practices = PracticePricing | 5 min | 🟡 Warning |
| 2.1 | SUM=0 | Global double-entry | 1 min | 🔴 Critical |
| 2.2 | SUM=0 | Per-practice balance | 5 min | 🔴 Critical |
| 3.1 | Computed | User.balance_user | 1 min | 🔴 Critical |
| 3.2 | Computed | frozen_amount | 1 min | 🔴 Critical |
| 3.3 | Computed | available_amount | 1 min | 🔴 Critical |
| 3.4 | Computed | current_participants | 5 min | 🟡 Warning |
| 3.5 | Computed | Promo.used_count | 5 min | 🟢 Info |
| 4.1 | Orphans | Bookings → Practice | 10 min | 🟡 Warning |
| 4.2 | Orphans | Bookings → User | 10 min | 🟡 Warning |
| 4.3 | Orphans | Purchases → User | 10 min | 🟡 Warning |
| 4.4 | Orphans | MasterLedger → User | 10 min | 🟡 Warning |
| 4.5 | Orphans | Deliveries → Notification | 10 min | 🟢 Info |
| 5.1 | Invariants | Frozen for completed | 5 min | 🔴 Critical |
| 5.2 | Invariants | Negative available | 1 min | 🔴 Critical |
| 5.3 | Invariants | Negative user balance | 1 min | 🔴 Critical |
| 5.4 | Invariants | Early attendance | 10 min | 🟢 Info |
| 5.5 | Invariants | Over max_participants | 5 min | 🟡 Warning |
| 5.6 | Invariants | Purchases without audit | 5 min | 🔴 Critical |

---

## 5. Реализация (будущее)

### MVP: Ручные проверки

В MVP семафоры — это SQL-скрипты, которые админ запускает вручную или через cron.

```bash
# cron job (каждые 5 минут)
*/5 * * * * psql -f /opt/velo/semaphores/run_all.sql >> /var/log/semaphores.log
```

### v2.0: Semaphore Service

```python
# semaphore_service.py
class SemaphoreService:
    semaphores = [
        Semaphore(
            name="bookings_purchases_active",
            query="SELECT ... ",
            frequency_seconds=60,
            criticality="critical"
        ),
        # ...
    ]
    
    async def run_all(self):
        results = []
        for sem in self.semaphores:
            result = await self.run_semaphore(sem)
            if result.status == "ALERT":
                await self.send_alert(sem, result)
            results.append(result)
        return results
    
    async def send_alert(self, sem: Semaphore, result: Result):
        if sem.criticality == "critical":
            await telegram.send(ADMIN_CHAT, f"🔴 {sem.name}: {result}")
        elif sem.criticality == "warning":
            await slack.send("#alerts", f"🟡 {sem.name}: {result}")
```

### При распиле на микросервисы

Каждый сервис экспортирует метрики:

```
GET /metrics/consistency
{
    "bookings_count_active": 1234,
    "bookings_count_cancelled": 56,
    "practices_count": 89
}
```

Semaphore Service собирает метрики со всех сервисов и сравнивает.

---

## 6. Добавление новых семафоров

При добавлении новой таблицы или связи, задай вопросы:

1. **1:1 связь?** → Добавь COUNT = COUNT семафор
2. **Кэшированное поле?** → Добавь Computed = Actual семафор
3. **FK на другую таблицу?** → Добавь Orphan Detection
4. **Бизнес-правило?** → Добавь Invariant семафор

---

**Конец документа**
