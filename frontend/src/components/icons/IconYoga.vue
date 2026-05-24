<template>
  <!-- TD-CAL-ICON-YOGA: placeholder yoga glyph, NOT a designer asset.
       Drawn in the set's filled / currentColor / viewBox-512 style so it
       can be swapped for the real icon later without any code change
       (same filename, same props, same viewBox). Figure: head + torso in
       a standing pose with arms raised overhead (namaste / tree pose). -->
  <svg xmlns="http://www.w3.org/2000/svg" :width="size" :height="size" viewBox="0 0 512 512" fill="currentColor">
    <!-- Head -->
    <path d="M256 16C282 16 303 37 303 63C303 89 282 110 256 110C230 110 209 89 209 63C209 37 230 16 256 16Z" />
    <!-- Raised arms meeting overhead (inverted V) + torso + legs in a wide stance -->
    <path d="M256 122C247 122 240 129 240 138L240 196L176 96C171 88 161 85 153 90C145 95 142 105 147 113L213 218C205 224 200 234 200 245L200 268L120 396C115 404 118 415 126 420C134 425 144 422 149 414L222 296L222 300C222 309 229 316 238 316L274 316C283 316 290 309 290 300L290 296L363 414C368 422 378 425 386 420C394 415 397 404 392 396L312 268L312 245C312 234 307 224 299 218L365 113C370 105 367 95 359 90C351 85 341 88 336 96L272 196L272 138C272 129 265 122 256 122Z" />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number | string }>(), { size: 24 })
</script>
