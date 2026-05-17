<script setup lang="ts">
import { useData } from 'vitepress'

const props = defineProps<{
  lightSrc: string
  darkSrc: string
  alt?: string
  width?: number
  height?: number
  caption?: string
}>()

const { isDark } = useData()
</script>

<template>
  <figure class="cb-dm-figure">
    <img
      :src="isDark ? darkSrc : lightSrc"
      :alt="alt || ''"
      :width="width"
      :height="height"
      class="cb-dm-image"
      loading="lazy"
    />
    <figcaption v-if="caption" class="cb-dm-caption">{{ caption }}</figcaption>
  </figure>
</template>

<style scoped>
.cb-dm-figure {
  margin: var(--cb-space-8) 0;
  text-align: center;
}

.cb-dm-image {
  max-width: 100%;
  height: auto;
  border-radius: var(--cb-radius-lg);
  border: 1px solid var(--cb-border);
  box-shadow: var(--cb-shadow-md);
  transition: opacity var(--cb-motion-normal), border-color var(--cb-motion-normal);
}

.cb-dm-image:hover {
  opacity: 0.95;
}

.cb-dm-caption {
  margin-top: var(--cb-space-3);
  font-size: 13px;
  color: var(--cb-text-3);
  font-style: italic;
}
</style>
