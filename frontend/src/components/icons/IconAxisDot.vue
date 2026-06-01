<!--
  VELO Frontend -- IconAxisDot (Diary map: between-cards axis connector)

  The small dot-line-dot link on the thread axis between two ordinary cards
  (Figma Vector 110): a top dot (r=1.33) + a thin stroke + a bottom dot
  (r=1.33). 1:1 from the export. Colour via currentColor.
-->
<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="3"
    :height="height"
    viewBox="0 0 3 18"
    fill="currentColor"
    aria-hidden="true"
  >
    <path d="M-2.03848e-05 16.333C-2.03848e-05 17.0694 0.596933 17.6663 1.33331 17.6663C2.06969 17.6663 2.66665 17.0694 2.66665 16.333C2.66665 15.5966 2.06969 14.9997 1.33331 14.9997C0.596933 14.9997 -2.03848e-05 15.5966 -2.03848e-05 16.333ZM-2.03848e-05 1.33301C-2.03848e-05 2.06939 0.596933 2.66634 1.33331 2.66634C2.06969 2.66634 2.66665 2.06939 2.66665 1.33301C2.66665 0.596628 2.06969 -0.000325561 1.33331 -0.000325561C0.596933 -0.000325561 -2.03848e-05 0.596628 -2.03848e-05 1.33301ZM1.33331 16.333H1.58331V1.33301H1.33331H1.08331V16.333H1.33331Z" />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Source is 3×18; keep ratio when only height is driven.
const props = withDefaults(defineProps<{ size?: number }>(), { size: 18 })
const height = computed(() => props.size)
</script>
