# VELO — Knowledge Base Changelog

All notable changes to this project knowledge base will be documented in this file.

---

## [2.1.0] - 2026-02-06

### Added
- **Knowledge Base Structure** — Created comprehensive project KB with 10 modules
  - `core.yaml` — Project vision, mission, problem/solution
  - `team.yaml` — Team structure, roles, decision log
  - `product.yaml` — Features, user stories, roadmap, edge cases
  - `tech.yaml` — Architecture, tech stack, database schema, deployment
  - `market.yaml` — Market analysis, competitors, GTM strategy
  - `customer.yaml` — Segments, personas, user journeys
  - `finances.yaml` — Revenue model, unit economics, projections
  - `marketing.yaml` — Positioning, messaging, channels, launch strategy
  - `roadmap.yaml` — Phases, sprints, milestones, backlog
  - `decisions.yaml` — Architecture Decision Records (ADRs)

### Context
- Project renamed from "YON Master Rooms" to VELO (February 2026)
- Technical specification exists (27 Dec 2025)
- Payment system design completed (5 Feb 2026)
- Mockups available (HTML prototypes)
- Ready for implementation phase

---

## [2.0.0] - 2026-02-05

### Added
- **Payment System Design** — Comprehensive financial architecture
  - Double-entry ledger system (3 journals: user/master/company)
  - Two promo code types (Company Promo vs Master Promo)
  - Refund policies
  - Withdrawal system

### Changed
- **Promo Economics** — Separated into two models
  - Company Promo: Master gets full 85%, company pays discount
  - Master Promo: Master reduces own revenue (5%/25%/50%/75%/100%)

### Decisions
- ADR-004: Double-entry ledger system (Accepted)
- ADR-005: Two promo types (Accepted)
- ADR-006: Manual withdrawal approval for MVP (Accepted)

---

## [1.1.0] - 2025-12-27

### Added
- **Master Profile JSONB Pattern** — Flexible master data structure
  - Verification flow (pending → verified → suspended → banned)
  - Availability toggle + auto-pause
  - 1:1 relationship with users table
- **Diagram 08** — Master verification state machine

### Changed
- **Database Schema** — Added master_profiles table with JSONB data column

---

## [1.0.0] - 2025-12-27

### Added
- **Initial Architecture Design**
  - 9 microservices defined (User, Practice, Quiz, Calendar, Notification, Booking, Payment, State, Library)
  - API Gateway pattern
  - JSONB credentials pattern for multi-platform users
  - APScheduler for calendar reminders
  - 7 Mermaid diagrams created

### Decisions
- ADR-001: Microservices architecture (Accepted)
- ADR-002: JSONB for credentials (Accepted)
- ADR-003: APScheduler for reminders (Accepted)
- ADR-007: Telegram bot for MVP (Accepted)
- ADR-008: Zoom for video (Accepted)
- ADR-009: PostgreSQL + Redis (Accepted)
- ADR-010: Stripe for payments (Accepted)

### Diagrams
1. Architecture Overview
2. API Flow: Booking Practice
3. Database Schema
4. Calendar Reminders (APScheduler)
5. Quiz Data Structure
6. Notification Service
7. User Credentials JSONB

---

## [0.1.0] - 2025-12-21

### Added
- **Initial Technical Specification** (Draft)
  - Executive summary
  - Problem statement
  - Core features (6 features)
  - Detailed functionality
  - Business model

---

## Upcoming Changes

### Next Release (3.0.0) — Implementation Start
- [ ] GitHub repository setup
- [ ] Sprint 1 kickoff (Infrastructure)
- [ ] Team recruitment finalized
- [ ] Beta master outreach

### Future (4.0.0) — Beta Launch
- [ ] 10 beta masters onboarded
- [ ] 50+ practices hosted
- [ ] NPS survey results

---

## Metadata

**Project Name:** VELO (renamed from YON Master Rooms, February 2026)
**Stage:** MVP / Pre-development
**Tier:** T2 (Sprout)
**KB Version:** 2.1.0
**KB Size:** ~15K tokens
**Last Updated:** 2026-02-06
