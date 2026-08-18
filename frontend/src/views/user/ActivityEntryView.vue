<!--
  VELO Frontend -- ActivityEntryView (B57, PROMPT No761)

  «Новое событие» -- capture an activity that happened outside the app's
  practice catalogue (yoga, a massage, an osteopath visit), optionally with a
  reflection. Reached from the Dashboard quick-access block (B55).

  Fields, in the owner's order:
    Когда произошло событие -- Дата + Время, REQUIRED, decides where the entry
                               sits in the diary's chronology
    Выбор активности        -- seed chips + own variant, REQUIRED
    Мое состояние           -- three-state MoodPicker, OPTIONAL
    Мысли                   -- reflection textarea, OPTIONAL
    Сохранить

  ⚠ `Сохранить` IS AN HONEST STUB AND THAT IS DELIBERATE, NOT UNFINISHED WORK.
  The form validates itself fully and then says the feature is not available
  yet, because the STORAGE CONTRACT DOES NOT EXIST -- the activity record, the
  per-user activity list and the mood value all imply schema that is with the
  backend teammate as a written primer (`docs/primer-b64-activity-schema.md`,
  B64). This project's own rule splits exactly here: a missing ACTION gets
  stubbed and shipped, a missing DATA CONTRACT is never invented
  (`velo_build_full_design`'s boundary). Wiring a save against a guessed shape
  is the one thing that rule forbids.

  Only PAST or CURRENT activities are recorded (owner's spec) -- a future
  date/time is rejected on submit. DatePickerSheet takes a `min` but no `max`,
  so the constraint lives in validation rather than in the sheet.
-->

<template>
  <div class="activity-entry">
    <VHeader title="Новое событие" show-back @back="router.back()" />

    <div class="activity-entry__content">
      <!-- Required-fields legend (DS banner, Phase-3) -- same plate and seal
           the master's create form uses; the design's own colours map onto
           these exact tokens. -->
      <div class="activity-entry__legend">
        <IconRequired class="activity-entry__legend-seal" :size="22" />
        <span>— поля, обязательные для заполнения</span>
      </div>

      <!-- ================= Когда произошло событие ================= -->
      <section class="activity-entry__section">
        <h3 class="activity-entry__section-title">Когда произошло событие</h3>

        <div class="activity-entry__field">
          <div class="activity-entry__field-row">
            <button
              type="button"
              class="activity-entry__picker"
              :class="{
                'activity-entry__picker--empty': !form.date,
                'activity-entry__picker--error': !!errors.date,
              }"
              @click="showDate = true"
            >
              {{ form.date ? dateDisplay : 'Дата' }}
            </button>
            <span
              class="activity-entry__seal"
              :class="{ 'activity-entry__seal--done': !!form.date }"
            >
              <IconRequired v-if="!form.date" :size="22" />
              <IconRequiredDone v-else :size="22" />
            </span>
          </div>
          <span v-if="errors.date" class="activity-entry__field-error">{{ errors.date }}</span>
        </div>

        <div class="activity-entry__field">
          <div class="activity-entry__field-row">
            <button
              type="button"
              class="activity-entry__picker"
              :class="{
                'activity-entry__picker--empty': !form.time,
                'activity-entry__picker--error': !!errors.time,
              }"
              @click="showTime = true"
            >
              {{ form.time || 'Время' }}
            </button>
            <span
              class="activity-entry__seal"
              :class="{ 'activity-entry__seal--done': !!form.time }"
            >
              <IconRequired v-if="!form.time" :size="22" />
              <IconRequiredDone v-else :size="22" />
            </span>
          </div>
          <span v-if="errors.time" class="activity-entry__field-error">{{ errors.time }}</span>
        </div>
      </section>

      <!-- ===================== Выбор активности ===================== -->
      <section class="activity-entry__section">
        <h3 class="activity-entry__section-title">Выбор активности</h3>

        <div class="activity-entry__field">
          <div class="activity-entry__field-row">
            <div class="activity-entry__card">
              <div class="activity-entry__chips">
                <VChip
                  v-for="name in SEED_ACTIVITIES"
                  :key="name"
                  size="md"
                  clickable
                  :active="form.seedActivity === name"
                  @click="pickSeed(name)"
                >
                  {{ name }}
                </VChip>
              </div>
              <VInput
                v-model="form.customActivity"
                class="activity-entry__own"
                label="Свой вариант активности"
                placeholder="Укажите ваш вариант"
                hide-label
                @update:model-value="onCustomInput"
              />
            </div>
            <span
              class="activity-entry__seal"
              :class="{ 'activity-entry__seal--done': !!chosenActivity }"
            >
              <IconRequired v-if="!chosenActivity" :size="22" />
              <IconRequiredDone v-else :size="22" />
            </span>
          </div>
          <span v-if="errors.activity" class="activity-entry__field-error">{{
            errors.activity
          }}</span>
        </div>
      </section>

      <!-- ====================== Мое состояние ====================== -->
      <section class="activity-entry__section">
        <h3 class="activity-entry__section-title">Мое состояние</h3>
        <MoodPicker v-model="form.mood" />
      </section>

      <!-- ========================== Мысли ========================== -->
      <section class="activity-entry__section">
        <h3 class="activity-entry__section-title">Мысли</h3>
        <VTextarea
          v-model="form.reflection"
          :rows="4"
          autogrow
          label="Мысли"
          hide-label
          placeholder="Напишите, что было важного. Вы можете вернуться к рефлексии позже"
        />
      </section>

      <VButton variant="primary" block size="lg" @click="submit">Сохранить</VButton>
    </div>

    <!-- Picker sheets (teleport to body; open on field tap). -->
    <DatePickerSheet
      :open="showDate"
      :model-value="form.date"
      title="Дата"
      @update:model-value="onDate"
      @close="showDate = false"
    />
    <TimePickerSheet
      :open="showTime"
      :model-value="form.time"
      title="Время"
      @update:model-value="onTime"
      @close="showTime = false"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { DateTime } from 'luxon'
import { VHeader } from '@/components/layout'
import { VButton, VChip, VInput, VTextarea } from '@/components/ui'
import { IconRequired, IconRequiredDone } from '@/components/icons'
import DatePickerSheet from '@/components/shared/DatePickerSheet.vue'
import TimePickerSheet from '@/components/shared/TimePickerSheet.vue'
import MoodPicker from '@/components/shared/MoodPicker.vue'
import { useToast } from '@/composables/useToast'
import { useViewerTimezone } from '@/composables/useViewerTimezone'
import { SEED_ACTIVITIES, type ActivityMood } from '@/utils/activityEntry'

const router = useRouter()
const toast = useToast()
const viewerTz = useViewerTimezone()

const showDate = ref(false)
const showTime = ref(false)

const form = reactive<{
  date: string
  time: string
  seedActivity: string
  customActivity: string
  mood: ActivityMood | null
  reflection: string
}>({
  date: '',
  time: '',
  seedActivity: '',
  customActivity: '',
  mood: null,
  reflection: '',
})

const errors = reactive<{ date: string; time: string; activity: string }>({
  date: '',
  time: '',
  activity: '',
})

/** One activity is chosen: either a seed chip or a typed own variant. The
 *  typed value wins, because typing is the later, more deliberate act. */
const chosenActivity = computed((): string => form.customActivity.trim() || form.seedActivity)

const dateDisplay = computed((): string =>
  form.date ? DateTime.fromISO(form.date).toFormat('dd.MM.yyyy') : '',
)

/** Picking a chip clears a half-typed own variant, so the two inputs can never
 *  disagree about what was chosen. */
function pickSeed(name: string): void {
  form.seedActivity = form.seedActivity === name ? '' : name
  if (form.seedActivity) form.customActivity = ''
  errors.activity = ''
}

function onCustomInput(): void {
  if (form.customActivity.trim()) form.seedActivity = ''
  errors.activity = ''
}

function onDate(value: string): void {
  form.date = value
  errors.date = ''
}

function onTime(value: string): void {
  form.time = value
  errors.time = ''
  // The future-rejection message lives on errors.date (it is about the DATE
  // field's own state, only decidable once both are known) -- changing the
  // time can resolve it, so drop it here too rather than leaving it stuck on
  // a field the user did not just touch. Never clears "Укажите дату".
  if (errors.date === FUTURE_MESSAGE) errors.date = ''
}

/** Past or current only -- the owner's spec excludes planning ahead. */
function isFuture(date: string, time: string): boolean {
  const at = DateTime.fromISO(`${date}T${time}`, { zone: viewerTz.value })
  return at.isValid && at > DateTime.now().setZone(viewerTz.value)
}

/** The one message the future check can produce -- named so onDate/onTime can
 *  tell "the combination was rejected" apart from "date is still empty" and
 *  clear only the former (found in verification: fixing the TIME alone left
 *  this message stuck on the DATE field until the date picker was re-opened). */
const FUTURE_MESSAGE = 'Можно записать только прошедшее событие'

function validate(): boolean {
  errors.date = form.date ? '' : 'Укажите дату'
  errors.time = form.time ? '' : 'Укажите время'
  errors.activity = chosenActivity.value ? '' : 'Выберите активность'
  if (!errors.date && !errors.time && isFuture(form.date, form.time)) {
    errors.date = FUTURE_MESSAGE
  }
  return !errors.date && !errors.time && !errors.activity
}

/**
 * The form enforces its own rules and then stops honestly. See the file
 * header: the storage contract is the gap, not the button.
 */
function submit(): void {
  if (!validate()) return
  toast.info('Функциональность пока недоступна')
}
</script>

<style scoped>
.activity-entry {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.activity-entry__content {
  padding: var(--space-2) 0 var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* -- Required-fields legend (DS, Phase-3) -- pink glass plate, rose seal.
   Mirrors CreatePracticeView's legend; the owner's 01.svg draws this exact
   plate (#F795A2 @ 0.4 fill, #AD3444 text, #D66674 seal), which are these
   tokens. -- */
.activity-entry__legend {
  display: flex;
  align-items: center;
  gap: var(--velo-banner-gap-icon-text);
  background: var(--velo-glass-pink-40);
  border: 1px solid var(--velo-pink-300);
  border-radius: 12px;
  padding: 10px var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--velo-pink-700);
}

.activity-entry__legend-seal {
  flex-shrink: 0;
  color: var(--velo-rating-good);
}

/* -- Section -- */
.activity-entry__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* Section headings are Regular 400, never bold: Marmelad ships one weight and
   the design fakes bold by stroking the glyphs. The app already ruled against
   that (UserDashboardView: «было 700 — баг-фикс»). */
.activity-entry__section-title {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0;
}

/* -- Field rows + required seal (shape shared with the master's create form) -- */
.activity-entry__field-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.activity-entry__field + .activity-entry__field {
  margin-top: var(--space-2);
}

.activity-entry__picker {
  flex: 1;
  min-width: 0;
  height: var(--velo-size-40);
  text-align: left;
  padding: 0 var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--velo-text-primary);
  background: var(--velo-bg-card-solid);
  border: 2px solid transparent;
  border-radius: var(--velo-radius-badge);
  cursor: pointer;
}

.activity-entry__picker--empty {
  color: var(--velo-text-muted);
}

.activity-entry__picker--error {
  border-color: var(--velo-error);
}

.activity-entry__seal {
  flex-shrink: 0;
  display: flex;
  color: var(--velo-error);
}

.activity-entry__seal--done {
  color: var(--velo-required-done);
}

.activity-entry__field-error {
  display: block;
  font-size: var(--text-xs);
  color: var(--velo-error);
  margin-top: var(--space-1);
}

/* -- Activity card -- */
.activity-entry__card {
  flex: 1;
  min-width: 0;
  background: var(--velo-bg-card-solid);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.activity-entry__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.activity-entry__own :deep(.v-input) {
  margin-bottom: 0;
}
</style>
