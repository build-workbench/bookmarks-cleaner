<script setup lang="ts">
import ThemedFigure from './ThemedFigure.vue'

defineProps<{
  lightSrc: string
  darkSrc: string
  alt?: string
  width?: number
  height?: number
  caption?: string
}>()
</script>

<template>
  <ThemedFigure
    :light-src="lightSrc"
    :dark-src="darkSrc"
    :alt="alt"
    :width="width"
    :height="height"
    :caption="caption"
  />
</template>
