# VELO Project Structure — Visual Map

```
velo/
├── 📋 README.md                              # Project overview
├── 📋 VELO-Payment-System-Meeting.md         # Payment system design (5 Feb 2026)
│
├── 🗂️ CORE/                                  # ⭐ Structured Knowledge Base (NEW)
│   ├── README.md                             # KB navigation guide
│   ├── CHANGELOG.md                          # Project history
│   │
│   ├── 📊 L0: Piles (Foundation)
│   │   ├── core.yaml                         # Vision, mission, problem/solution
│   │   └── team.yaml                         # Roles, structure, culture
│   │
│   ├── 📊 L1: Foundation
│   │   ├── product.yaml                      # Features, user stories, roadmap
│   │   ├── market.yaml                       # TAM/SAM/SOM, competitors, GTM
│   │   ├── customer.yaml                     # Personas, journey, segments
│   │   └── finances.yaml                     # Revenue model, unit economics
│   │
│   ├── 📊 L2: Walls (Execution)
│   │   ├── marketing.yaml                    # Positioning, channels, launch
│   │   └── roadmap.yaml                      # Phases, sprints, backlog
│   │
│   └── 📊 Meta
│       └── decisions.yaml                    # ADRs (Architecture Decision Records)
│
├── 🗂️ tech_spec/                             # Technical Documentation
│   ├── index.md                              # Documentation index
│   ├── tech_task.md                          # Main technical specification
│   ├── master-rooms-specification.md         # Business requirements
│   ├── master-rooms-architecture-v2.md       # Detailed architecture
│   ├── user-model-jsonb-pattern.md           # User model deep dive
│   ├── master-profile-jsonb-pattern.md       # Master profile deep dive
│   │
│   └── 📁 diagrams/                          # 8 Mermaid Diagrams
│       ├── 01-architecture-overview.mermaid  # High-level architecture
│       ├── 02-api-flow-booking.mermaid       # Booking sequence diagram
│       ├── 03-database-schema.mermaid        # ER diagram
│       ├── 04-calendar-reminders.mermaid     # APScheduler workflow
│       ├── 05-quiz-data-structure.mermaid    # Quiz JSON structure
│       ├── 06-notification-service.mermaid   # Notification architecture
│       ├── 07-user-credentials-jsonb.mermaid # JSONB pattern
│       └── 08-master-verification-flow.mermaid # Verification state machine
│
└── 🗂️ velo-mockups/                          # UI Prototypes (HTML)
    ├── README.md                             # Mockup usage guide
    ├── index.html                            # Landing page
    ├── user.html                             # User interface prototype
    ├── master.html                           # Master dashboard prototype
    ├── admin.html                            # Admin panel prototype
    ├── 📁 css/                               # Stylesheets
    └── 📁 js/                                # JavaScript
```

---

## 📚 Documentation Map

### 🎯 For Quick Start
```
Start Here: CORE/README.md → Your role guide
```

### 👔 For Product Owner / Stakeholder
```
1. CORE/core.yaml          (What & Why)
2. CORE/product.yaml       (Features & Roadmap)
3. CORE/finances.yaml      (Business Model)
4. tech_spec/index.md      (Technical Overview)
```

### 💻 For Tech Lead / Backend Dev
```
1. CORE/tech.yaml                         (Architecture & Stack)
2. CORE/decisions.yaml                    (Why these decisions)
3. tech_spec/tech_task.md                 (Detailed spec)
4. tech_spec/diagrams/                    (Visual architecture)
5. tech_spec/*-jsonb-pattern.md           (Implementation patterns)
```

### 📊 For Marketing / Growth
```
1. CORE/market.yaml        (Market Analysis)
2. CORE/customer.yaml      (Personas & Journey)
3. CORE/marketing.yaml     (Go-to-Market)
4. velo-mockups/           (UI Prototypes)
```

### 💰 For Finance / Founder
```
1. CORE/finances.yaml                     (Revenue Model & Projections)
2. VELO-Payment-System-Meeting.md         (Payment System Design)
3. CORE/core.yaml                         (Vision, Risks, Assumptions)
```

---

## 🎨 Layer Architecture (CCC)

```
L3 (Roof)          ┌──────────────────────────────────┐
Tech Stack         │  tech.yaml                       │
                   │  - 9 microservices               │
                   │  - PostgreSQL + Redis            │
                   │  - FastAPI, Stripe, Zoom         │
                   └──────────────────────────────────┘

L2 (Walls)         ┌──────────────────────────────────┐
Execution          │  marketing.yaml, roadmap.yaml    │
                   │  - 6 phases, 10 sprints          │
                   │  - GTM strategy                  │
                   └──────────────────────────────────┘

L1 (Foundation)    ┌──────────────────────────────────┐
Business Layer     │  product, market, customer,      │
                   │  finances                        │
                   │  - Features, personas, model     │
                   └──────────────────────────────────┘

L0 (Piles)         ┌──────────────────────────────────┐
Core               │  core.yaml, team.yaml            │
                   │  - Vision, mission, problem      │
                   │  - Team structure                │
                   └──────────────────────────────────┘
                              ⛔ Gate: Must be >3.0/5
```

---

## 📊 Knowledge Distribution

```
Total Documentation: ~200KB

CORE/ (Structured KB)      ████████░░ 85KB (43%)
├─ Strategic (L0-L1)       ████░░░░░░ 40KB (20%)
├─ Tactical (L2)           ██░░░░░░░░ 20KB (10%)
└─ Meta (Decisions)        ██░░░░░░░░ 25KB (13%)

tech_spec/                 ████████░░ 80KB (40%)
├─ Specifications          ████░░░░░░ 50KB (25%)
├─ Patterns                ██░░░░░░░░ 20KB (10%)
└─ Diagrams                █░░░░░░░░░ 10KB (5%)

velo-mockups/              ███░░░░░░░ 35KB (17%)
├─ HTML/CSS/JS             ███░░░░░░░ 35KB (17%)
```

---

## 🔗 Cross-References

### Payment System
```
VELO-Payment-System-Meeting.md
    ↓
CORE/finances.yaml (revenue model)
    ↓
CORE/decisions.yaml (ADR-004: Double-entry)
    ↓
tech_spec/master-rooms-architecture-v2.md (Payment Service)
```

### User Management
```
tech_spec/user-model-jsonb-pattern.md
    ↓
CORE/tech.yaml (database schema: users table)
    ↓
CORE/decisions.yaml (ADR-002: JSONB credentials)
    ↓
tech_spec/diagrams/07-user-credentials-jsonb.mermaid
```

### Master Verification
```
tech_spec/master-profile-jsonb-pattern.md
    ↓
CORE/product.yaml (Master Verification feature)
    ↓
tech_spec/diagrams/08-master-verification-flow.mermaid
```

---

## 📅 Document Timeline

```
Dec 21, 2025   tech_spec/master-rooms-specification.md    (Initial spec)
Dec 27, 2025   tech_spec/tech_task.md                     (Architecture v1.0)
Dec 27, 2025   tech_spec/diagrams/* (8 diagrams)          (Visual architecture)
Jan 27, 2026   velo-mockups/*                             (UI prototypes)
Feb 5, 2026    VELO-Payment-System-Meeting.md             (Payment design)
Feb 6, 2026    CORE/* (10 modules)                        (Structured KB v2.1)
```

---

## 🎯 Next Evolution

### Planned Additions
```
CORE/
├── risks.yaml                    # Detailed risk register
├── pilots.yaml                   # Beta program details
└── brand/                        # Brand guidelines (future)
    ├── voice.yaml
    ├── visual.yaml
    └── assets/
```

### Integration Points
```
GitHub repo (TBD)
    ↓
CI/CD pipeline
    ↓
Documentation as Code
    ↓
Auto-generate from CORE/*.yaml
```

---

## 🔍 Search Index

### By Role
- **Product Owner:** core.yaml, product.yaml, roadmap.yaml
- **Tech Lead:** tech.yaml, decisions.yaml, tech_spec/
- **Marketing:** market.yaml, marketing.yaml, customer.yaml
- **Finance:** finances.yaml, VELO-Payment-System-Meeting.md
- **Designer:** velo-mockups/, customer.yaml (personas)

### By Phase
- **Pre-kickoff:** CORE/core.yaml, CORE/team.yaml
- **Sprint Planning:** CORE/roadmap.yaml
- **Development:** tech_spec/, CORE/tech.yaml
- **Launch:** CORE/marketing.yaml
- **Scaling:** CORE/finances.yaml (projections)

### By Topic
- **Architecture:** decisions.yaml (ADRs), tech_spec/tech_task.md
- **Payments:** VELO-Payment-System-Meeting.md, finances.yaml
- **User Flow:** customer.yaml, tech_spec/diagrams/02-*
- **Database:** tech.yaml, tech_spec/03-database-schema.mermaid
- **Monetization:** finances.yaml, core.yaml

---

## 📊 Health Status

### Documentation Coverage
```
✅ Vision & Mission         100% (core.yaml)
✅ Team Structure           100% (team.yaml)
✅ Product Features         100% (product.yaml)
✅ Technical Architecture   100% (tech.yaml)
✅ Market Analysis          100% (market.yaml)
✅ Customer Research        100% (customer.yaml)
✅ Financial Model          100% (finances.yaml)
✅ Marketing Strategy       100% (marketing.yaml)
✅ Roadmap                  100% (roadmap.yaml)
✅ Decision Records         100% (decisions.yaml, 10 ADRs)
```

### Implementation Status
```
⏳ Infrastructure           0% (Sprint 1: Weeks 1-2)
⏳ Core Services            0% (Sprint 2-3: Weeks 3-6)
⏳ Automation               0% (Sprint 4-5: Weeks 7-10)
⏳ Analytics                0% (Sprint 6-7: Weeks 11-14)
⏳ Beta Launch              0% (Sprint 9: Weeks 17-18)
```

---

**Last Updated:** 2026-02-06
**Maintained By:** Project Team
**Format Version:** 2.1.0
