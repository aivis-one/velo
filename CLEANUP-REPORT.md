# VELO — Cleanup Report

**Дата:** 6 февраля 2026
**Статус:** ✅ Обновления внесены

---

## ✅ Выполненные обновления

### 1. Обновлена финансовая логика (frozen/available)

**Изменения в CORE/:**
- ✅ `finances.yaml` — добавлен механизм frozen/available split
- ✅ `tech.yaml` — обновлены схемы master_profiles и master_ledger
- ✅ `decisions.yaml` — обновлен ADR-004, добавлен ADR-011 "Commission Only From Live Money"
- ✅ `decisions.yaml` — Q-001 закрыт (решение принято: комиссия от фактической суммы)

**Ключевые изменения:**
```yaml
Master Balance теперь состоит из:
- frozen_amount: Деньги, ожидающие завершения практики
- available_amount: Деньги, доступные для вывода

Комиссия: 15% только от "живых денег" (что реально заплатил юзер)
```

**Источник:** `/velo/VELO-Payment-System-Meeting.md` (обновлен 6 Feb, статус: ✅ Утверждено)

---

### 2. Очищены упоминания YON

**Замены:**
- ❌ "YON Master Rooms" → ✅ "VELO" (название проекта)
- ❌ "YON community" → ✅ "VELO community"
- ❌ "YON ecosystem" → ✅ "VELO ecosystem"
- ❌ "YON app" → ✅ "VELO app"
- ❌ "внутри экосистемы YON" → ✅ удалено/переформулировано

**Сохранены (корректные упоминания):**
- ✅ "YON State Engine" — внешний API (интеграция остается)

**Обновлены файлы:**
```
CORE/
├── core.yaml                 ✅ project_name: "VELO"
├── market.yaml               ✅ VELO community/ecosystem
├── marketing.yaml            ✅ VELO ecosystem/app
├── customer.yaml             ✅ VELO community/app
├── finances.yaml             ✅ VELO ecosystem/community
├── product.yaml              ✅ убрано "внутри YON"
├── roadmap.yaml              ✅ VELO community
├── decisions.yaml            ✅ VELO community
├── README.md                 ✅ "VELO" (без YON)
└── CHANGELOG.md              ✅ renamed from "YON Master Rooms"

Корень:
├── README.md                 ✅ "VELO — Mermaid Diagrams"

tech_spec/
└── index.md                  ✅ "VELO — Documentation Index"
```

---

## 📋 Рекомендации по файлам

### Временные файлы (можно удалить)

```
/mnt/cowork/
├── VELO-KB-Analysis.md           [17KB] 🗑️ Временный отчет для демонстрации
└── velo-project-dashboard.html   [18KB] 🗑️ Временный дашборд для демонстрации
```

**Рекомендация:** Удалить оба файла из `/mnt/cowork/` (они были созданы для демонстрации KB).

**Если нужно сохранить:**
- Переместить в `/velo/docs/` или `/velo/CORE/reports/`
- Или держать в корне cowork/, если используются как точка входа

---

### Дублирующие файлы

**README.md в корне velo/**
- Содержит: "VELO — Mermaid Diagrams" (описание диаграмм)
- Статус: ✅ Актуален, но возможно стоит переименовать в `DIAGRAMS.md`
- Рекомендация: **Оставить** (актуален для навигации по diagrams/)

**project-structure.md в CORE/**
- Содержит: Визуальную карту структуры проекта
- Статус: ✅ Актуален
- Рекомендация: **Оставить** (полезен для навигации)

---

### Устаревшие файлы tech_spec/

**Файлы с упоминаниями YON (не обновлены полностью):**
```
tech_spec/
├── master-rooms-architecture-v2.md    ⚠️  Содержит "YON Master Rooms"
├── master-rooms-specification.md      ⚠️  Содержит много "YON Master Rooms"
├── tech_task.md                       ⚠️  Заголовок "YON Master Rooms"
├── user-model-jsonb-pattern.md        ✅  Технический, YON не упоминается
└── master-profile-jsonb-pattern.md    ✅  Технический, YON не упоминается
```

**Рекомендация:**
- ✅ **Оставить как есть** (это архивные спецификации с датами декабрь 2025)
- ✅ Добавить в заголовок файлов: `(Legacy — renamed to VELO, Feb 2026)`
- ❌ НЕ удалять (важная документация по архитектуре)

**Пример:**
```markdown
# YON Master Rooms — Technical Specification (Legacy)

**Note:** Project was renamed to VELO in February 2026.
**Current docs:** See `/CORE/` for up-to-date information.
```

---

### .idea/ папка (IDE artifacts)

```
/velo/.idea/   [IntelliJ IDEA config]
```

**Рекомендация:**
- 🗑️ **Добавить в .gitignore** (если еще не добавлено)
- 🗑️ **Удалить из репозитория:** `git rm -r --cached .idea/`

---

## 🎯 План действий

### Immediate (сейчас)

```bash
# 1. Удалить временные файлы
rm /mnt/cowork/VELO-KB-Analysis.md
rm /mnt/cowork/velo-project-dashboard.html

# 2. Добавить .idea в .gitignore (если нет)
echo ".idea/" >> /velo/.gitignore

# 3. Удалить .idea из git (если закоммичена)
cd /velo
git rm -r --cached .idea/
git commit -m "Remove IDE artifacts from repo"
```

### Optional (опционально)

```bash
# 4. Добавить legacy-notice в старые tech_spec файлы
# (вручную редактировать заголовки master-rooms-*.md)

# 5. Переименовать README.md → DIAGRAMS.md (для ясности)
cd /velo
mv README.md DIAGRAMS.md
```

---

## 📊 Итоговая статистика

**Обновлено файлов:** 14
**Удалить рекомендуется:** 2-3
**Оставить как legacy:** 3 (tech_spec)

**До:**
- Упоминаний "YON Master Rooms": ~50
- Упоминаний "YON community/ecosystem": ~20

**После:**
- Упоминаний "YON Master Rooms" в актуальных docs: 0 ✅
- Упоминаний "YON State Engine" (корректно): ~10 ✅

---

## ✅ Checklist финальной проверки

- [x] frozen/available логика добавлена в CORE/
- [x] ADR-004 обновлен
- [x] ADR-011 создан ("Commission Only From Live Money")
- [x] Q-001 закрыт (решение принято)
- [x] "YON Master Rooms" → "VELO" в CORE/
- [x] "YON community/ecosystem" → "VELO" в CORE/
- [x] README.md (корень velo/) обновлен
- [x] tech_spec/index.md обновлен
- [ ] .idea/ удалена из git
- [ ] Временные файлы удалены из /mnt/cowork/
- [ ] Legacy notice добавлен в старые tech_spec (опционально)

---

**Prepared by:** Claude
**Date:** 2026-02-06
**Status:** Ready for review
