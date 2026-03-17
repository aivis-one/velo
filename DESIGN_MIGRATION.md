# VELΘ Design Migration Plan v4
# Старт от main. Никаких ссылок на старые ветки.

> **Рабочая ветка:** создать `design/veltheta` от `main`
> **Деплой теста:** VPS переключить на `design/veltheta`, `velo update`
> **Все задания выполняет Claude Code** в рабочей ветке

---

## Принципы

1. Имена CSS-переменных не трогать — только значения справа от `:`
2. Новые переменные — добавлять в конец `variables.css`, не переименовывать старые
3. Фон — через `body { background }` в `global.css` (импортируется в `main.ts` → попадает в JS-бандл, Telegram не кеширует)
4. Каждое задание = точный код, без интерпретации

---

## Полный список файлов (37 штук, проверено по коду)

```
СТИЛИ
  frontend/src/styles/variables.css
  frontend/src/styles/global.css
  frontend/index.html

UI-КОМПОНЕНТЫ (изменить существующие)
  frontend/src/components/ui/VButton.vue
  frontend/src/components/ui/VInput.vue
  frontend/src/components/ui/VCard.vue
  frontend/src/components/ui/VBadge.vue
  frontend/src/components/ui/VProgressBar.vue
  frontend/src/components/ui/VeloLogo.vue

UI-КОМПОНЕНТЫ (создать новые)
  frontend/src/components/ui/VTag.vue
  frontend/src/components/ui/VNotification.vue
  frontend/src/components/ui/VToggle.vue
  frontend/src/components/ui/VAccordion.vue
  frontend/src/components/ui/index.ts  (добавить 4 экспорта)

ИКОНКИ (создать новые Vue-компоненты)
  frontend/src/components/ui/icons/IconHome.vue
  frontend/src/components/ui/icons/IconCalendar.vue
  frontend/src/components/ui/icons/IconDiary.vue
  frontend/src/components/ui/icons/IconProfile.vue
  frontend/src/components/ui/icons/IconDashboard.vue
  frontend/src/components/ui/icons/IconPractices.vue
  frontend/src/components/ui/icons/IconAnalytics.vue
  frontend/src/components/ui/icons/IconBrain.vue
  frontend/src/components/ui/icons/IconGroup.vue
  frontend/src/components/ui/icons/IconFeedback.vue
  frontend/src/components/ui/icons/IconClock.vue

LAYOUT
  frontend/src/components/layout/MobileLayout.vue
  frontend/src/components/layout/AdminLayout.vue
  frontend/src/components/layout/VTabBar.vue
  frontend/src/components/layout/VHeader.vue
  frontend/src/router/tabs.ts

VIEWS — AUTH/STANDALONE
  frontend/src/views/auth/LoadingView.vue
  frontend/src/views/auth/StandaloneStubView.vue
  frontend/src/views/NotFoundView.vue

VIEWS — MASTER (отдельный фон)
  frontend/src/views/master/MasterApplyView.vue

SHARED COMPONENTS
  frontend/src/components/shared/PracticeCard.vue
  frontend/src/components/shared/BookingCard.vue
  frontend/src/components/shared/BookingPopup.vue
```

**Остальные views (user/*, master/*, admin/*) автоматически получают новый вид** через обновлённые CSS-переменные из DS-1 и обновлённые компоненты. Отдельно их трогать не нужно — только точечные правки если что-то сломается.

---

## DS-1: variables.css

**Файл:** `frontend/src/styles/variables.css`

Заменить только значения, имена не трогать:

```css
/* === Colors: Primary === */
--velo-primary: #627a9c;
--velo-primary-light: #627a9c;
--velo-primary-dark: #4c6589;

/* === Colors: Background === */
--velo-bg-start: #ffffff;
--velo-bg-end: #ffffff;
--velo-bg-subtle: rgba(98, 122, 156, 0.06);
--velo-bg-card: #ffffff;

/* === Colors: Text === */
--velo-text-primary: #4c6589;
--velo-text-secondary: rgba(76, 101, 137, 0.70);
--velo-text-muted: rgba(76, 101, 137, 0.50);

/* === Colors: Borders === */
--velo-border: #abbfda;
--velo-border-light: rgba(171, 191, 218, 0.30);

/* === Colors: Semantic base === */
--velo-success: #76dde6;
--velo-warning: #fbc088;
--velo-error: #f795a2;
--velo-info: #76dde6;

/* === Colors: Semantic tints === */
--velo-warning-bg: rgba(251, 192, 136, 0.40);
--velo-warning-bg-hover: rgba(251, 192, 136, 0.55);
--velo-warning-border: #fbc088;
--velo-warning-text: #a16124;
--velo-warning-text-light: #d4863c;

--velo-error-bg: rgba(253, 226, 226, 0.40);
--velo-error-bg-subtle: rgba(253, 226, 226, 0.40);
--velo-error-border: #f795a2;
--velo-error-text: #a16124;

--velo-success-bg: rgba(118, 221, 230, 0.40);
--velo-success-text: #26767d;

--velo-info-bg: rgba(118, 221, 230, 0.40);
--velo-info-text: #2f9ea8;

/* === Colors: Mood === */
--velo-mood-low: #f795a2;
--velo-mood-mid: #fbc088;
--velo-mood-high: #76dde6;

/* === Typography === */
--font-body: 'Marmelad', 'Noto Sans', sans-serif;
--font-heading: 'Marmelad', 'Noto Sans', sans-serif;

--text-xs: 14px;
--text-sm: 15px;
--text-base: 18px;
--text-lg: 20px;
--text-xl: 32px;
--text-2xl: 50px;
--text-3xl: 32px;

/* === Spacing === */
--space-1: 4px;
--space-2: 8px;
--space-3: 14px;
--space-4: 16px;
--space-5: 24px;
--space-6: 24px;
--space-8: 33px;
--space-10: 48px;

/* === Borders === */
--radius-sm: 15px;
--radius-md: 15px;
--radius-lg: 15px;
--radius-xl: 100px;
--radius-full: 9999px;   ← НЕ ТРОГАТЬ

/* === Shadows === */
--shadow-sm: none;
--shadow-md: none;
--shadow-lg: none;
--shadow-xl: none;
```

Добавить в конец файла (новые переменные):

```css
/* === VELΘ: Glass colors === */
--velo-glass-blue-15: rgba(98, 122, 156, 0.15);
--velo-glass-blue-60: rgba(171, 191, 218, 0.60);
--velo-glass-teal-30: rgba(118, 221, 230, 0.30);
--velo-glass-teal-40: rgba(118, 221, 230, 0.40);
--velo-glass-peach-40: rgba(251, 192, 136, 0.40);
--velo-glass-white-01: rgba(255, 255, 255, 0.01);

/* === VELΘ: Primitive palette === */
--velo-teal-400: #76dde6;
--velo-teal-600: #2f9ea8;
--velo-teal-700: #26767d;
--velo-peach-300: #fbc088;
--velo-peach-500: #d4863c;
--velo-peach-700: #a16124;
--velo-pink-300: #f795a2;
--velo-pink-100: #fde2e2;
--velo-blue-100: #e2f0fd;
--velo-blue-200: #abbfda;
--velo-sand-100: #fdf3e2;

/* === VELΘ: Glow shadow === */
--velo-shadow-glow: 0px 0px 20.9px 7px #ffffff;

/* === VELΘ: Layout === */
--velo-content-width: 336px;
--velo-screen-width: 402px;
--velo-screen-padding: 33px;

/* === VELΘ: Navigation === */
--velo-nav-active-bg: #627a9c;
--velo-nav-inactive-bg: rgba(98, 122, 156, 0.15);

/* === VELΘ: Z-index background === */
--z-background: -1;
--z-content: 1;
```

---

## DS-2: global.css + index.html + 3 views с фоном

### `frontend/index.html`

Найти строки с Inter и Playfair Display, заменить на:
```html
<link href="https://fonts.googleapis.com/css2?family=Marmelad&display=swap" rel="stylesheet">
```

### `frontend/src/styles/global.css`

Заменить весь файл:

```css
/* =============================================================================
 * VELΘ Frontend — Global Styles
 * =========================================================================== */

/* === Reset === */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* === Base === */
html {
  font-size: var(--text-base);
  -webkit-text-size-adjust: 100%;
  -webkit-tap-highlight-color: transparent;
}

body {
  font-family: var(--font-body);
  font-weight: 400;
  font-size: var(--text-base);
  letter-spacing: 0.02em;
  line-height: 1.5;
  color: var(--velo-text-primary);
  background: url('/bg/background.png') center / cover no-repeat fixed;
  overscroll-behavior: none;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* === Typography === */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-body);
  font-weight: 400;
  line-height: 1.3;
  letter-spacing: 0.02em;
  color: var(--velo-text-primary);
}

a {
  color: var(--velo-primary);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* === Images === */
img, svg {
  display: block;
  max-width: 100%;
}

/* === Buttons reset === */
button {
  font-family: inherit;
  font-size: inherit;
  cursor: pointer;
  border: none;
  background: none;
  padding: 0;
  color: inherit;
}

/* === Inputs reset === */
input, select, textarea {
  font-family: inherit;
  font-size: inherit;
  color: inherit;
}

/* === Lists === */
ul, ol {
  list-style: none;
}

/* === Scrollbar === */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--velo-blue-200);
  border-radius: var(--radius-full);
}
```

### Фоновое изображение

Скопировать `Design_prototype/assets/backgrounds/background.png` в `frontend/public/bg/background.png`.

### `frontend/src/views/auth/LoadingView.vue`

В `<style scoped>` найти `.loading {` и убрать строку `background: var(--velo-bg-start);`

### `frontend/src/views/auth/StandaloneStubView.vue`

В `<style scoped>` найти `.stub {` и убрать строку `background: var(--velo-bg-start);`

### `frontend/src/views/NotFoundView.vue`

В `<style scoped>` найти `.not-found {` и убрать строку `background: var(--velo-bg-start);`

### `frontend/src/views/master/MasterApplyView.vue`

В `<style scoped>` найти `.apply-view {` и заменить:
```css
/* было */
background: linear-gradient(135deg, var(--velo-bg-start) 0%, var(--velo-bg-end) 100%);
/* стало */
background: transparent;
```

---

## DS-3: UI Components

### `frontend/src/components/ui/VButton.vue`

**`<script setup>`** — заменить тип `variant` и `size`, убрать `block`:
```typescript
withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
    size?: 'sm' | 'md'
    disabled?: boolean
    loading?: boolean
  }>(),
  {
    variant: 'primary',
    size: 'md',
    disabled: false,
    loading: false,
  },
)
```

**`<template>`** — убрать `'v-btn--block': block` из `:class`.

**`<style scoped>`** — полная замена:
```css
.v-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  width: 100%;
  font-family: var(--font-body);
  font-weight: 400;
  letter-spacing: 0.02em;
  border: 1px solid #ffffff;
  border-radius: var(--radius-full);
  cursor: pointer;
  position: relative;
  white-space: nowrap;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  box-shadow: var(--velo-shadow-glow);
  transition: transform var(--transition-fast), opacity var(--transition-fast);
}
.v-btn--md {
  height: 50px;
  font-size: var(--text-lg);
  padding: 0 var(--space-5);
}
.v-btn--sm {
  height: 36px;
  font-size: var(--text-sm);
  padding: 0 var(--space-4);
  width: auto;
}
.v-btn--primary {
  background: var(--velo-primary);
  color: #ffffff;
}
.v-btn--secondary {
  background: var(--velo-glass-blue-60);
  color: var(--velo-text-primary);
}
.v-btn--ghost {
  background: var(--velo-glass-white-01);
  color: var(--velo-text-primary);
}
.v-btn--danger {
  background: var(--velo-error);
  color: #ffffff;
}
.v-btn:active:not(:disabled) {
  transform: scale(0.97);
}
.v-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.v-btn--loading {
  cursor: wait;
}
.v-btn__content--hidden {
  visibility: hidden;
}
.v-btn__spinner {
  position: absolute;
  width: 18px;
  height: 18px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: v-btn-spin 0.6s linear infinite;
}
@keyframes v-btn-spin {
  to { transform: rotate(360deg); }
}
```

**Grep и замени по всему `frontend/src/`:**
- `variant="outline"` → `variant="ghost"`
- `size="lg"` → `size="md"`
- `:block="true"` → убрать атрибут
- `block` как standalone атрибут на `<VButton` → убрать

---

### `frontend/src/components/ui/VInput.vue`

**`<script setup>`** — убрать проп `error?: string`.

**`<template>`** — убрать:
- `:class="{ 'v-input--error': !!error }"` с корневого div
- `<span v-if="error" class="v-input__error">{{ error }}</span>`

**`<style scoped>`** — полная замена:
```css
.v-input {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}
.v-input__label {
  display: block;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  letter-spacing: 0.02em;
  color: var(--velo-text-secondary);
}
.v-input__field {
  width: 100%;
  height: 40px;
  padding: 0 var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  letter-spacing: 0.02em;
  color: var(--velo-text-primary);
  background: #ffffff;
  border: none;
  border-radius: 5px;
  outline: none;
  transition: border var(--transition-fast);
}
.v-input__field:focus {
  border: 2px solid var(--velo-border);
}
.v-input__field::placeholder {
  color: var(--velo-text-muted);
}
.v-input__field:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
```

**Grep по всему `frontend/src/`:** найти `:error=` на `<VInput` → удалить проп.

---

### `frontend/src/components/ui/VCard.vue`

**`<style scoped>`** — заменить `.v-card`:
```css
.v-card {
  background: #ffffff;
  border: none;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  transition: transform var(--transition-fast);
}
.v-card--clickable {
  cursor: pointer;
}
.v-card--clickable:active {
  transform: scale(0.98);
}
.v-card--no-padding {
  padding: 0;
}
```

---

### `frontend/src/components/ui/VBadge.vue`

**`<style scoped>`** — полная замена (сейчас hardcoded hex):
```css
.v-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  height: 23px;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  letter-spacing: 0.02em;
  border-radius: 71px;
  white-space: nowrap;
}
.v-badge--success {
  background: var(--velo-glass-teal-30);
  color: var(--velo-teal-600);
}
.v-badge--warning {
  background: var(--velo-glass-peach-40);
  color: var(--velo-peach-700);
}
.v-badge--error {
  background: var(--velo-pink-100);
  color: var(--velo-pink-300);
}
.v-badge--info {
  background: var(--velo-blue-100);
  color: var(--velo-text-primary);
}
```

---

### `frontend/src/components/ui/VProgressBar.vue`

В `<style scoped>` заменить только `.v-progress__track`:
```css
.v-progress__track {
  flex: 1;
  height: 8px;
  background: var(--velo-glass-blue-15);
  border-radius: var(--radius-full);
  overflow: hidden;
}
```

---

### `frontend/src/components/ui/VeloLogo.vue`

Заменить fallback:
```html
<!-- было -->
fill="var(--velo-primary, #334D6E)"
<!-- стало -->
fill="var(--velo-primary, #627a9c)"
```

---

### НОВЫЙ: `frontend/src/components/ui/VTag.vue`

```vue
<!--
  VELΘ Frontend -- VTag Component
  Pill-shaped category label.
  Variants: blue | pink | sand
-->
<template>
  <span class="v-tag" :class="`v-tag--${variant}`">
    <slot />
  </span>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{ variant?: 'blue' | 'pink' | 'sand' }>(),
  { variant: 'blue' },
)
</script>

<style scoped>
.v-tag {
  display: inline-flex;
  align-items: center;
  height: 19px;
  padding: 0 8px;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  letter-spacing: 0.02em;
  color: var(--velo-text-primary);
  border-radius: var(--radius-full);
  white-space: nowrap;
}
.v-tag--blue  { background: var(--velo-blue-100); }
.v-tag--pink  { background: var(--velo-pink-100); }
.v-tag--sand  { background: var(--velo-sand-100); }
</style>
```

---

### НОВЫЙ: `frontend/src/components/ui/VNotification.vue`

```vue
<!--
  VELΘ Frontend -- VNotification Component
  Inline notification banner. Replaces per-field error states in forms.
  Variants: warning | success
-->
<template>
  <div v-if="title" class="v-notification" :class="`v-notification--${variant}`">
    <div class="v-notification__title">{{ title }}</div>
    <div v-if="body" class="v-notification__body">{{ body }}</div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'warning' | 'success'
    title?: string
    body?: string
  }>(),
  { variant: 'warning' },
)
</script>

<style scoped>
.v-notification {
  width: 100%;
  min-height: 66px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.v-notification--warning {
  background: var(--velo-warning-bg);
  border: 2px solid var(--velo-warning-border);
}
.v-notification--success {
  background: var(--velo-success-bg);
  border: 2px solid var(--velo-success);
}
.v-notification__title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  letter-spacing: 0.02em;
}
.v-notification--warning .v-notification__title { color: var(--velo-warning-text); }
.v-notification--success .v-notification__title { color: var(--velo-success-text); }
.v-notification__body {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  letter-spacing: 0.02em;
}
.v-notification--warning .v-notification__body { color: var(--velo-warning-text-light); }
.v-notification--success .v-notification__body { color: var(--velo-info-text); }
</style>
```

---

### НОВЫЙ: `frontend/src/components/ui/VToggle.vue`

```vue
<!--
  VELΘ Frontend -- VToggle Component
  Segmented control. Used in AI-summary (Неделя / Месяц).
-->
<template>
  <div class="v-toggle">
    <button
      v-for="opt in options"
      :key="opt.value"
      class="v-toggle__item"
      :class="{ 'v-toggle__item--active': modelValue === opt.value }"
      @click="$emit('update:modelValue', opt.value)"
    >{{ opt.label }}</button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  options: Array<{ value: string; label: string }>
}>()
defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<style scoped>
.v-toggle {
  display: inline-flex;
  height: 30px;
  background: var(--velo-glass-blue-15);
  border-radius: var(--radius-full);
  padding: 2px;
  gap: 2px;
}
.v-toggle__item {
  flex: 1;
  padding: 0 14px;
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  letter-spacing: 0.02em;
  color: var(--velo-text-primary);
  border-radius: var(--radius-full);
  border: none;
  background: transparent;
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
  white-space: nowrap;
}
.v-toggle__item--active {
  background: var(--velo-primary);
  color: #ffffff;
}
</style>
```

---

### НОВЫЙ: `frontend/src/components/ui/VAccordion.vue`

```vue
<!--
  VELΘ Frontend -- VAccordion Component
  Expandable row. Used in Practice Detail.
-->
<template>
  <div class="v-accordion">
    <button class="v-accordion__header" @click="open = !open">
      <span class="v-accordion__title">{{ title }}</span>
      <span class="v-accordion__icon" :class="{ 'v-accordion__icon--open': open }">▾</span>
    </button>
    <Transition name="v-accordion">
      <div v-show="open" class="v-accordion__body">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
defineProps<{ title: string }>()
const open = ref(false)
</script>

<style scoped>
.v-accordion {
  width: 100%;
  background: #ffffff;
  border-radius: var(--radius-md);
  overflow: hidden;
}
.v-accordion__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 14px 16px;
  background: none;
  border: none;
  cursor: pointer;
}
.v-accordion__title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  letter-spacing: 0.02em;
  color: var(--velo-text-primary);
}
.v-accordion__icon {
  font-size: 18px;
  color: var(--velo-text-primary);
  transition: transform 250ms cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}
.v-accordion__icon--open { transform: rotate(180deg); }
.v-accordion__body {
  padding: 0 16px 14px;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  letter-spacing: 0.02em;
  color: var(--velo-text-secondary);
  line-height: 1.5;
}
.v-accordion-enter-active { transition: opacity 250ms cubic-bezier(0.4, 0, 0.2, 1); }
.v-accordion-leave-active { transition: opacity 150ms cubic-bezier(0.4, 0, 1, 1); }
.v-accordion-enter-from, .v-accordion-leave-to { opacity: 0; }
</style>
```

---

### `frontend/src/components/ui/index.ts`

Добавить в конец файла:
```typescript
export { default as VTag } from './VTag.vue'
export { default as VNotification } from './VNotification.vue'
export { default as VToggle } from './VToggle.vue'
export { default as VAccordion } from './VAccordion.vue'
```

---

## DS-4: Layout Components

### `frontend/src/components/layout/MobileLayout.vue`

В `<style scoped>` заменить `.mobile-layout`:
```css
.mobile-layout {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  min-height: 100vh;
  background: transparent;
}
.mobile-layout__main {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  -webkit-overflow-scrolling: touch;
}
```

---

### `frontend/src/components/layout/AdminLayout.vue`

В `<style scoped>` заменить `.admin-layout`:
```css
.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  min-height: 100vh;
  background: transparent;
}
.admin-layout__main {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  -webkit-overflow-scrolling: touch;
}
```

---

### `frontend/src/components/layout/VHeader.vue`

**`<style scoped>`** — полная замена:
```css
.v-header {
  position: sticky;
  top: 0;
  z-index: var(--z-sticky, 200);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  background: transparent;
  min-height: 56px;
}
.v-header__left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}
.v-header__back {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 36px;
  font-size: var(--text-lg);
  color: var(--velo-text-primary);
  border-radius: var(--radius-full);
  border: 1px solid #ffffff;
  background: var(--velo-glass-blue-15);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  flex-shrink: 0;
  transition: opacity var(--transition-fast);
}
.v-header__back:active { opacity: 0.7; }
.v-header__title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  letter-spacing: 0.02em;
  color: var(--velo-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.v-header__badge {
  background: var(--velo-primary);
  color: white;
  font-size: var(--text-xs);
  font-weight: 400;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}
.v-header__right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}
```

---

### `frontend/src/components/layout/VTabBar.vue`

**`<style scoped>`** — полная замена:
```css
.v-tabbar {
  position: sticky;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 8px 20px;
  padding-bottom: calc(8px + env(safe-area-inset-bottom, 0px));
  background: transparent;
  z-index: var(--z-sticky, 200);
}
.v-tabbar__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 63px;
  height: 63px;
  border-radius: 50%;
  border: 1.26px solid #ffffff;
  color: var(--velo-text-primary);
  transition: background var(--transition-fast);
  position: relative;
  cursor: pointer;
}
.v-tabbar__item--active {
  background: var(--velo-nav-active-bg);
  color: #ffffff;
}
.v-tabbar__item:not(.v-tabbar__item--active) {
  background: var(--velo-nav-inactive-bg);
  backdrop-filter: blur(2.52px);
  -webkit-backdrop-filter: blur(2.52px);
}
.v-tabbar__icon {
  font-size: 22px;
  line-height: 1;
}
.v-tabbar__label {
  font-family: var(--font-body);
  font-size: 10px;
  font-weight: 400;
  letter-spacing: 0.02em;
  margin-top: 2px;
}
.v-tabbar__badge {
  position: absolute;
  top: 6px;
  right: 6px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--velo-error);
  color: white;
  font-size: 9px;
  font-weight: 400;
  border-radius: var(--radius-full);
}
```

---

## DS-5: Иконки для VTabBar

В `Design_prototype/assets/icons/` есть: `icon-calendar.svg`, `icon-clock.svg`, `icon-diary.svg`, `icon-feedback.svg`, `icon-group.svg`, `icon-brain.svg`, `icon-profile.svg`.

Для VTabBar нужны иконки которых нет в Design_prototype. Создать простые SVG-компоненты:

### `frontend/src/components/ui/icons/IconHome.vue`
```vue
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 9.5L12 3L21 9.5V20C21 20.55 20.55 21 20 21H15V15H9V21H4C3.45 21 3 20.55 3 20V9.5Z" fill="currentColor"/>
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 24 })
</script>
```

### `frontend/src/components/ui/icons/IconBookings.vue`
```vue
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM7 7H17V9H7V7ZM7 11H17V13H7V11ZM7 15H13V17H7V15Z" fill="currentColor"/>
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 24 })
</script>
```

Иконки из Design_prototype обернуть в Vue-компоненты по такому же шаблону:
- `icon-calendar.svg` → `IconCalendar.vue`
- `icon-diary.svg` → `IconDiary.vue`
- `icon-profile.svg` → `IconProfile.vue`
- `icon-brain.svg` → `IconBrain.vue`
- `icon-group.svg` → `IconGroup.vue`
- `icon-feedback.svg` → `IconFeedback.vue`
- `icon-clock.svg` → `IconClock.vue`

Шаблон обёртки для каждого:
```vue
<template>
  <svg :width="size" :height="size" viewBox="..." fill="none" xmlns="...">
    <!-- содержимое из .svg файла -->
  </svg>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 24 })
</script>
```

### `frontend/src/router/tabs.ts`

Заменить emoji на компоненты пока нельзя (TabItem.icon — строка). Оставить emoji как есть. После DS-5 при желании можно рефакторить TabItem чтобы принимал компонент — это отдельная задача.

---

## DS-6: Shared Components

### `frontend/src/components/shared/PracticeCard.vue`

В `<style scoped>`:
- `.practice-card`: `border: none`, `border-radius: var(--radius-md)`
- `.practice-card:hover`: убрать `box-shadow: 0 8px 24px rgba(51, 77, 110, 0.12)`
- `.practice-card__title`: `font-weight: 400`
- `.practice-card__price`: `font-weight: 400`

### `frontend/src/components/shared/BookingCard.vue`

В `<style scoped>`:
- `.booking-card`: `border: none`, `border-radius: var(--radius-md)`
- `.booking-card__title`: `font-weight: 400`

### `frontend/src/components/shared/BookingPopup.vue`

В `<style scoped>`:
- `.popup__title`: `font-family: var(--font-body)`, `font-weight: 400`

---

## Порядок выполнения и деплоя

```
1. DS-1 → деплой → проверить что ничего не сломалось, цвета сдвинулись
2. DS-2 → деплой → проверить фон виден
3. DS-3 → деплой → проверить кнопки и инпуты
4. DS-4 → деплой → проверить навбар и хедер
5. DS-5 → деплой → проверить иконки (необязательно, emoji работают)
6. DS-6 → деплой → проверить карточки практик и бронирований
```

После каждого деплоя — скриншот, если что-то не так — чинить до следующей фазы.

---

## Что НЕ меняем

- Всю бизнес-логику, сторы, API
- TypeScript-типы
- Структуру шаблонов (только стили)
- Admin views — получат новый вид автоматически через DS-1
- `frontend/src/views/user/*` и `frontend/src/views/master/*` — получат новый вид через DS-1 + DS-3 + DS-6 автоматически. Трогать только если есть видимые сломы после деплоя DS-6.
