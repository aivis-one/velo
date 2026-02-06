# VELO Project Knowledge Base

**Version:** 2.1.0
**Created:** 2026-02-06
**Stage:** MVP / Pre-development
**Tier:** T2 (Sprout)

---

## 📋 Что это?

Структурированная база знаний проекта **VELO** — платформы для wellness-фасилитаторов и практикующих.

Формат совместим с **project-builder v9.0** (система управления проектными знаниями).

---

## 🗂️ Структура

### Основные модули (L0-L1: Foundation)

| Файл | Содержание | Для кого |
|------|-----------|----------|
| **core.yaml** | Vision, mission, problem/solution | Все |
| **team.yaml** | Роли, структура, культура | HR, PM |
| **product.yaml** | Фичи, user stories, roadmap | Product, Dev |
| **tech.yaml** | Архитектура, стек, БД | Tech Lead, Dev |
| **market.yaml** | Рынок, конкуренты, GTM | Marketing, Sales |
| **customer.yaml** | Сегменты, персоны, journey | Product, Marketing |
| **finances.yaml** | Модель доходов, unit economics | Finance, Founder |

### Поддержка (L2-L3: Execution)

| Файл | Содержание | Для кого |
|------|-----------|----------|
| **marketing.yaml** | Позиционирование, каналы, запуск | Marketing |
| **roadmap.yaml** | Фазы, спринты, бэклог | PM, Dev |
| **decisions.yaml** | ADR (Architecture Decision Records) | Tech Lead, Архитектор |
| **CHANGELOG.md** | История изменений проекта | Все |

---

## 🎯 Быстрый старт

### Для Product Owner / Stakeholder
**Читать:**
1. `core.yaml` — что мы делаем и почему
2. `product.yaml` — какие фичи и почему
3. `roadmap.yaml` — когда и как

### Для Tech Lead / Backend Dev
**Читать:**
1. `tech.yaml` — архитектура, стек, схема БД
2. `decisions.yaml` — почему приняли эти решения
3. `roadmap.yaml` — план спринтов

### Для Marketing / Growth
**Читать:**
1. `market.yaml` — рынок, конкуренты, сегменты
2. `customer.yaml` — персоны, user journey
3. `marketing.yaml` — позиционирование, каналы

### Для Finance / Founder
**Читать:**
1. `finances.yaml` — модель доходов, проекции
2. `core.yaml` — vision, risks, assumptions

---

## 📊 Ключевые метрики

**Project Stage:** MVP
**Target Launch:** Week 20 (5 месяцев)
**Team Size:** 5-7 человек
**Initial Funding Need:** $500K (seed) или bootstrapped

**Year 1 Goals:**
- 1,000 мастеров
- $1M GMV/month
- $150K revenue/month (15% commission)

---

## 🏗️ Архитектура (кратко)

**Pattern:** Microservices (9 сервисов + API Gateway)
**Stack:** FastAPI + PostgreSQL + Redis
**Deployment:** Docker + Kubernetes
**Payments:** Stripe
**Video:** Zoom API
**Analytics:** YON State Engine integration

**Services:**
1. User Service (auth, multi-platform)
2. Practice Service (CRUD, pricing)
3. Quiz Service (pre/post practice)
4. Calendar Service (reminders, APScheduler)
5. Notification Service (multi-channel)
6. Booking Service (reservations)
7. Payment Service (double-entry ledger)
8. State Service (YON integration)
9. Library Service (video recordings)

---

## 💰 Бизнес-модель

**Revenue:** 15% комиссия с практик
**Promo Types:**
- Company Promo (компания платит мастеру полную долю)
- Master Promo (мастер снижает свой доход)

**Ledger System:** Double-entry (3 журнала: user/master/company)

---

## 🚀 Roadmap (кратко)

| Phase | Weeks | Goal |
|-------|-------|------|
| Phase 0: Foundation | 1-2 | Infrastructure setup |
| Phase 1: Core Services | 3-6 | User, Practice, Booking, Payment |
| Phase 2: Automation | 7-10 | Calendar, Notifications, Zoom |
| Phase 3: Analytics | 11-14 | YON State, Dashboards |
| Phase 4: Verification | 15-16 | Master verification, Promo |
| Phase 5: Beta | 17-18 | 10 masters, 50+ practices |
| Phase 6: Launch | 19-20 | Public release |

---

## 📚 Связанные документы

**В проекте (../tech_spec/):**
- `tech_task.md` — Техническое задание (подробное)
- `master-rooms-specification.md` — Бизнес-требования
- `master-rooms-architecture-v2.md` — Детальная архитектура
- `VELO-Payment-System-Meeting.md` — Дизайн платёжной системы
- `diagrams/` — 8 Mermaid-диаграмм (архитектура, API, БД, flow)

**Mockups (../velo-mockups/):**
- `index.html` — Landing page
- `user.html` — User interface prototype
- `master.html` — Master dashboard prototype
- `admin.html` — Admin panel prototype

---

## 🔄 Версионирование

**Current Version:** 2.1.0
**Last Updated:** 2026-02-06

См. `CHANGELOG.md` для истории изменений.

---

## 🤝 Контакты

**Communication:**
- Slack: `#master-rooms-dev`
- GitHub: [TBD]
- Figma: [TBD]

**Team:**
- Product Owner: TBD
- Tech Lead: TBD
- Backend Dev: TBD
- Frontend Dev: TBD
- DevOps: TBD

---

## 📖 Как использовать эту KB

### Обновление данных
Редактируйте YAML файлы напрямую. Формат человекочитаемый.

### Аудит проекта
```bash
# Проверить здоровье проекта
project-builder audit
```

### Экспорт документов
```bash
# Создать pitch deck или one-pager
project-builder export pitch
project-builder export summary
```

### Создание project skill
```bash
# Упаковать KB в Claude skill для контекста
project-builder build-skill
```

---

## ⚠️ Открытые вопросы

1. **Master Promo commission** — от полной или фактической цены? (см. `decisions.yaml`)
2. **S3 provider** — AWS S3 или CloudFlare R2? (deadline: Week 8)
3. **K8s hosting** — AWS EKS, GCP GKE, или DigitalOcean? (deadline: Week 12)
4. **Minimum withdrawal** — $10, $50, или без лимита?

См. `decisions.yaml → open_questions` для деталей.

---

## 📝 Next Actions

**Immediate:**
- [ ] Finalize tech decisions (S3, K8s hosting)
- [ ] Setup GitHub repo
- [ ] Recruit beta masters (VELO community)
- [ ] Draft onboarding guides

**Week 1:**
- [ ] Kickoff meeting
- [ ] Sprint 1 planning (Infrastructure)
- [ ] Assign service ownership
- [ ] Setup dev environment

---

**Maintained by:** Project Team
**Format:** project-builder v9.0 compatible
**License:** Internal use only
