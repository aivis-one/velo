# YON Master Rooms — Documentation Index

**Project:** YON Master Rooms MVP  
**Version:** 1.0 (Draft)  
**Date:** December 27, 2025  
**Status:** Architecture Design Phase  

---

## 📋 Main Documents

### 1. **tech_task.md** — Technical Specification ⭐ START HERE

**Что внутри:**
- Architectural decisions (микросервисы, JSONB, APScheduler)
- Services breakdown (9 сервисов + API Gateway)
- Database design
- Technology stack
- API design principles
- Deployment strategy
- Testing strategy
- Next steps (roadmap по неделям)

**Для кого:** Все — заказчик, разработчики, DevOps

**Файл:** `tech_task.md`

---

### 2. **master-rooms-specification.md** — Business Requirements

**Что внутри:**
- Executive summary
- Problem statement (боли мастеров и пользователей)
- Core features (6 ключевых функций)
- Detailed functionality (8 разделов)
- Business model (трёхсторонняя платформа)
- Monetization (5 потоков доходов)

**Для кого:** Заказчик, product manager, маркетинг

**Файл:** `master-rooms-specification.md`

---

### 3. **master-rooms-architecture-v2.md** — Detailed Architecture

**Что внутри:**
- Service responsibilities (детальное описание каждого сервиса)
- Database schemas (SQLAlchemy 2.0 models)
- API endpoints (примеры request/response)

**Для кого:** Бэкенд-разработчики

**Файл:** `master-rooms-architecture-v2.md`

---

### 4. **user-model-jsonb-pattern.md** — User Model Deep Dive

**Что внутри:**
- JSONB credentials pattern (почему и как)
- SQL schema с индексами
- SQLAlchemy 2.0 model (с helper methods)
- Usage examples (create, query, multi-platform)
- Performance benchmarks
- Migration strategy

**Для кого:** Бэкенд-разработчики (User Service implementation)

**Файл:** `user-model-jsonb-pattern.md`

---

### 5. **master-profile-jsonb-pattern.md** — Master Profile Deep Dive

**Что внутри:**
- JSONB data pattern для мастеров
- Account status & verification flow
- Availability management (simple toggle + auto-pause)
- SQL schema с индексами
- SQLAlchemy 2.0 model (с helper methods)
- Usage examples (verification, suspension, stats update)
- Migration strategy (JSONB → relational)

**Для кого:** Бэкенд-разработчики (Master verification, profile management)

**Файл:** `master-profile-jsonb-pattern.md`

---

## 📊 Mermaid Diagrams

### Architecture & Services

**01. Architecture Overview**
- Общая архитектура (9 сервисов + gateway)
- Data layer (PostgreSQL, Redis)
- External services (Zoom, Stripe, YON, S3)

**Файл:** `diagrams/01-architecture-overview.mermaid`

---

**02. API Flow: Booking Practice**
- Sequence diagram полного booking flow
- От выбора практики до получения Zoom link
- Включает quiz, payment check, notifications

**Файл:** `diagrams/02-api-flow-booking.mermaid`

---

**03. Database Schema**
- ER-диаграмма основных таблиц
- Все связи (foreign keys)
- Обновлённая версия с JSONB credentials

**Файл:** `diagrams/03-database-schema.mermaid`

---

### Calendar & Notifications

**04. Calendar Reminders**
- APScheduler workflow
- Как планируются напоминания (24h, 1h, 10min)
- Отмена при изменении статуса практики

**Файл:** `diagrams/04-calendar-reminders.mermaid`

---

**06. Notification Service**
- Архитектура Notification Service
- 4 типа отправки (user/channel/group/thread)
- Priority queue + retry logic
- State diagram (pending → sent/failed)

**Файл:** `diagrams/06-notification-service.mermaid`

---

### Data Structures

**05. Quiz Data Structure**
- Class diagram структуры квизов
- 5 типов вопросов (scale, emotion, choice, multi, text)
- Примеры JSON (questions & answers)

**Файл:** `diagrams/05-quiz-data-structure.mermaid`

---

**07. User Credentials JSONB**
- JSONB structure (telegram/web/discord)
- Sequence diagrams (first login, add platform, multi-platform)
- Index strategy (GIN + partial indexes)
- Migration path (state diagram)

**Файл:** `diagrams/07-user-credentials-jsonb.mermaid`

---

**08. Master Verification Flow**
- State diagram верификации мастеров
- Статусы: pending → verified → suspended → banned
- Описание каждого состояния

**Файл:** `diagrams/08-master-verification-flow.mermaid`

---

## 🗂️ Document Structure

```
/outputs/
├── tech_task.md                          # ⭐ Main spec
├── master-rooms-specification.md         # Business requirements
├── master-rooms-architecture-v2.md       # Detailed architecture
├── user-model-jsonb-pattern.md           # User model deep dive
├── master-profile-jsonb-pattern.md       # Master profile deep dive
├── index.md                              # This file
│
└── diagrams/
    ├── README.md                         # Diagrams usage guide
    ├── 01-architecture-overview.mermaid
    ├── 02-api-flow-booking.mermaid
    ├── 03-database-schema.mermaid
    ├── 04-calendar-reminders.mermaid
    ├── 05-quiz-data-structure.mermaid
    ├── 06-notification-service.mermaid
    ├── 07-user-credentials-jsonb.mermaid
    └── 08-master-verification-flow.mermaid
```

---

## 🎯 Quick Start Guide

### For Product Owner / Stakeholder

**Читать в таком порядке:**
1. `master-rooms-specification.md` — что мы делаем и почему
2. `tech_task.md` (разделы: Architecture, Services, Next Steps) — как реализуем
3. `diagrams/01-architecture-overview.mermaid` — визуализация архитектуры

---

### For Backend Developer

**Читать в таком порядке:**
1. `tech_task.md` — общая картина (Technology Stack, Services, API Design)
2. `master-rooms-architecture-v2.md` — детали каждого сервиса
3. `diagrams/03-database-schema.mermaid` — структура БД
4. `user-model-jsonb-pattern.md` (если работаешь с User Service)
5. Specific diagrams для своего сервиса (04, 05, 06, 07)

---

### For Frontend Developer

**Читать в таком порядке:**
1. `tech_task.md` (разделы: Services, API Design) — какие API будут
2. `diagrams/02-api-flow-booking.mermaid` — пример полного flow
3. `diagrams/05-quiz-data-structure.mermaid` — структура квизов для UI
4. `master-rooms-specification.md` (Detailed Functionality) — UI requirements

---

### For DevOps Engineer

**Читать в таком порядке:**
1. `tech_task.md` (разделы: Technology Stack, Deployment, Monitoring)
2. `diagrams/01-architecture-overview.mermaid` — что деплоить
3. `tech_task.md` (Infrastructure section) — Docker Compose + K8s

---

## 📝 TODO: Missing Documentation

### Services (ещё не детально описаны)

- [ ] **Booking Service** — детальная документация
- [ ] **Payment Service** — Stripe integration guide
- [ ] **State Service** — YON State Engine integration
- [ ] **Library Service** — S3/CDN setup

### Diagrams (ещё не созданы)

- [ ] **Payment Flow** — Stripe subscription + one-time payments
- [ ] **State Service Flow** — check-in/check-out + YON API
- [ ] **Library Upload Flow** — запись практики → S3 → CDN
- [ ] **Deployment Diagram** — Docker Compose + K8s architecture

### API Specs (ещё не финализированы)

- [ ] **OpenAPI/Swagger specs** для каждого сервиса
- [ ] **Request/Response examples** для всех endpoints
- [ ] **Error codes** — полный справочник

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2025-12-27 | JSONB patterns finalized |
| | | - MasterProfile JSONB structure |
| | | - Verification flow (pending → verified → suspended/banned) |
| | | - Availability toggle + auto-pause |
| | | - 1:1 relationships (user_id as PK) |
| | | - Diagram 08: Master verification flow |
| 1.0 | 2025-12-27 | Initial architecture design |
| | | - 9 microservices defined |
| | | - JSONB credentials pattern |
| | | - APScheduler for calendar |
| | | - 7 Mermaid diagrams created |

---

## 📞 Contacts

**Team:**
- Product Owner: [TBD]
- Tech Lead: [TBD]
- Backend Dev: [TBD]
- Frontend Dev: [TBD]

**Communication:**
- Slack: #master-rooms-dev
- GitHub: [repo URL]
- Figma: [design URL]

---

## 🚀 Next Meeting Agenda

**Обсудить:**
1. ✅ Architecture approval (9 microservices + JSONB)
2. ⏳ Open questions (Zoom limits, S3 provider, K8s hosting)
3. ⏳ Sprint planning (кто берёт какой сервис)
4. ⏳ Design review (UI mockups для web MVP)

**Принять решения:**
- [ ] Платные практики на MVP? (да/нет)
- [ ] Комиссия платформы (фиксированная 20% или кастомизируемая?)
- [ ] Сертификация мастеров (верификация или open marketplace?)

---

**Last Updated:** December 27, 2025
