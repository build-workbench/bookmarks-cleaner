<script setup lang="ts">
import { useData } from 'vitepress'

const props = defineProps<{
  lightSrc: string
  darkSrc: string
  alt?: string
  width?: number
  height?: number
}>()

const { isDark } = useData()
</script>

<template>
  <img
    :src="isDark ? darkSrc : lightSrc"
    :alt="alt || ''"
    :width="width"
    :height="height"
    class="dark-mode-image"
  />
</template>

<style scoped>
.dark-mode-image {
  transition: opacity 0.3s ease;
}

.dark-mode-image:hover {
  opacity: 0.9;
}
</style>
