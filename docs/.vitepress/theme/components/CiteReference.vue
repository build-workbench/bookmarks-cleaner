<script setup lang="ts">
// CiteReference - 学术引用组件
// 用于在文档中添加学术引用标记

const props = defineProps<{
  id: string | number
  authors: string
  title: string
  venue?: string
  year?: number
  url?: string
}>()
</script>

<template>
  <span class="citation-wrapper">
    <sup class="citation-ref">
      <a v-if="url" :href="url" target="_blank" rel="noopener">[{{ id }}]</a>
      <span v-else>[{{ id }}]</span>
    </sup>
    <span class="citation-tooltip">
      <span class="citation-authors">{{ authors }}</span>
      <span class="citation-title">"{{ title }}"</span>
      <span v-if="venue" class="citation-venue">{{ venue }}</span>
      <span v-if="year" class="citation-year">({{ year }})</span>
    </span>
  </span>
</template>

<style scoped>
.citation-wrapper {
  position: relative;
  display: inline;
}

.citation-ref {
  font-size: 11px;
  vertical-align: super;
  line-height: 0;
}

.citation-ref a {
  color: var(--vp-c-brand-1);
  text-decoration: none;
  font-weight: 500;
  padding: 0 2px;
  border-radius: 3px;
  transition: all 0.15s ease;
}

.citation-ref a:hover {
  background: var(--vp-c-brand-soft);
}

.citation-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 12px;
  background: var(--vp-c-bg-elv);
  border: 1px solid var(--vp-c-border);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 100;
  pointer-events: none;
}

.citation-wrapper:hover .citation-tooltip {
  opacity: 1;
  visibility: visible;
}

.citation-authors {
  color: var(--vp-c-text-1);
  font-weight: 500;
}

.citation-title {
  color: var(--vp-c-text-2);
  margin-left: 4px;
}

.citation-venue {
  color: var(--vp-c-brand-1);
  font-style: italic;
  margin-left: 4px;
}

.citation-year {
  color: var(--vp-c-text-3);
  margin-left: 4px;
}
</style>
