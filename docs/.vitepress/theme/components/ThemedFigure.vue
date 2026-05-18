<script setup lang="ts">
withDefaults(defineProps<{
  lightSrc: string
  darkSrc?: string
  alt?: string
  width?: number
  height?: number
  caption?: string
}>(), {
  alt: '',
})
</script>

<template>
  <figure class="cb-figure">
    <picture class="cb-figure-picture">
      <source
        v-if="darkSrc"
        :srcset="darkSrc"
        media="(prefers-color-scheme: dark)"
      >
      <img
        class="cb-figure-image"
        :src="lightSrc"
        :alt="alt"
        :width="width"
        :height="height"
        loading="lazy"
        decoding="async"
      >
    </picture>
    <figcaption v-if="caption" class="cb-figure-caption">{{ caption }}</figcaption>
  </figure>
</template>

<style scoped>
.cb-figure {
  margin: 2rem 0;
}

.cb-figure-picture {
  display: block;
  border: 1px solid var(--cb-border);
  border-radius: 20px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--cb-accent) 3%, transparent), transparent 24%),
    var(--cb-bg-elevated);
  overflow: hidden;
  box-shadow: var(--cb-shadow-md);
}

.cb-figure-image {
  display: block;
  width: 100%;
  height: auto;
}

.cb-figure-caption {
  margin-top: 0.75rem;
  color: var(--cb-text-3);
  font-size: 0.875rem;
  line-height: 1.6;
  text-align: center;
}
</style>
