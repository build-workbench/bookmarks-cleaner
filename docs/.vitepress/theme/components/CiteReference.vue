<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  id: string | number
  authors: string
  title: string
  venue?: string
  year?: number
  url?: string
}>()

const showTooltip = ref(false)

function toggleTooltip() {
  showTooltip.value = !showTooltip.value
}

function closeTooltip() {
  showTooltip.value = false
}
</script>

<template>
  <span class="cb-cite-wrapper">
    <sup class="cb-cite-ref">
      <a
        v-if="url"
        :href="url"
        target="_blank"
        rel="noopener noreferrer"
        @click.stop
      >[{{ id }}]</a>
      <span v-else @click.stop="toggleTooltip" class="cb-cite-clickable">[{{ id }}]</span>
    </sup>
    <span
      v-if="showTooltip || url"
      class="cb-cite-tooltip"
      :class="{ 'cb-cite-tooltip-active': showTooltip }"
      @click.stop
    >
      <span class="cb-cite-authors">{{ authors }}</span>
      <span class="cb-cite-title">"{{ title }}"</span>
      <span v-if="venue" class="cb-cite-venue">{{ venue }}</span>
      <span v-if="year" class="cb-cite-year">({{ year }})</span>
      <button v-if="!url" class="cb-cite-close" @click.stop="closeTooltip">&times;</button>
    </span>
  </span>
</template>

<style scoped>
.cb-cite-wrapper {
  position: relative;
  display: inline;
}

.cb-cite-ref {
  font-size: 11px;
  vertical-align: super;
  line-height: 0;
}

.cb-cite-ref a,
.cb-cite-clickable {
  color: var(--cb-accent);
  text-decoration: none;
  font-weight: 600;
  padding: 1px 4px;
  border-radius: 4px;
  transition: all var(--cb-motion-fast);
  cursor: pointer;
}

.cb-cite-ref a:hover,
.cb-cite-clickable:hover {
  background: var(--cb-accent-soft);
}

.cb-cite-tooltip {
  position: absolute;
  bottom: 130%;
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  padding: 10px 14px;
  background: var(--cb-bg-elevated);
  border: 1px solid var(--cb-border);
  border-radius: 10px;
  box-shadow: var(--cb-shadow-lg);
  font-size: 12px;
  line-height: 1.5;
  max-width: 320px;
  white-space: normal;
  opacity: 0;
  visibility: hidden;
  transition: all var(--cb-motion-normal);
  z-index: 100;
  pointer-events: none;
  text-align: left;
}

.cb-cite-tooltip-active {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
  pointer-events: auto;
}

.cb-cite-wrapper:hover .cb-cite-tooltip:not(.cb-cite-tooltip-active) {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
  pointer-events: auto;
}

.cb-cite-authors {
  color: var(--cb-text);
  font-weight: 600;
  display: block;
  margin-bottom: 2px;
}

.cb-cite-title {
  color: var(--cb-text-2);
  display: block;
  margin-bottom: 2px;
}

.cb-cite-venue {
  color: var(--cb-accent);
  font-style: italic;
}

.cb-cite-year {
  color: var(--cb-text-3);
  margin-left: 4px;
}

.cb-cite-close {
  position: absolute;
  top: 4px;
  right: 6px;
  background: none;
  border: none;
  color: var(--cb-text-muted);
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
}

.cb-cite-close:hover {
  color: var(--cb-text);
  background: var(--cb-bg-soft);
}

@media (max-width: 640px) {
  .cb-cite-tooltip {
    position: fixed;
    bottom: auto;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    max-width: 90vw;
    width: 280px;
  }

  .cb-cite-tooltip-active {
    transform: translate(-50%, -50%);
  }

  .cb-cite-wrapper:hover .cb-cite-tooltip:not(.cb-cite-tooltip-active) {
    opacity: 0;
    visibility: hidden;
  }
}
</style>
