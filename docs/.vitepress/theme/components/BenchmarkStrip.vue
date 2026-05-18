<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'
import { getLandingContent } from '../home-content.mjs'

const { lang } = useData()
const locale = computed(() => lang.value === 'zh-CN' ? 'zh' : 'en')
const content = computed(() => getLandingContent(locale.value))
</script>

<template>
  <section class="cb-benchmark-strip">
    <article
      v-for="item in content.metrics"
      :key="item.label"
      class="cb-benchmark-item"
    >
      <p class="cb-benchmark-label">{{ item.label }}</p>
      <p class="cb-benchmark-value">{{ item.value }}</p>
      <p class="cb-benchmark-note">{{ item.note }}</p>
    </article>
  </section>
</template>

<style scoped>
.cb-benchmark-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.9rem;
  margin: 2rem 0 2.5rem;
}

.cb-benchmark-item {
  padding: 1rem 1.15rem;
  border-radius: 18px;
  border: 1px solid var(--cb-border);
  background: var(--cb-bg-elevated);
  box-shadow: var(--cb-shadow-sm);
}

.cb-benchmark-label,
.cb-benchmark-value,
.cb-benchmark-note {
  margin: 0;
}

.cb-benchmark-label {
  color: var(--cb-text-3);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.cb-benchmark-value {
  margin-top: 0.55rem;
  color: var(--cb-text);
  font-size: 1.3rem;
  font-weight: 800;
}

.cb-benchmark-note {
  margin-top: 0.5rem;
  color: var(--cb-text-3);
  font-size: 0.9rem;
  line-height: 1.5;
}

@media (max-width: 960px) {
  .cb-benchmark-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .cb-benchmark-strip {
    grid-template-columns: 1fr;
  }
}
</style>
