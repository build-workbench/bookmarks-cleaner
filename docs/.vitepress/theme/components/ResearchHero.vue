<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'
import { getLandingContent } from '../home-content.mjs'

const { lang } = useData()
const locale = computed(() => lang.value === 'zh-CN' ? 'zh' : 'en')
const content = computed(() => getLandingContent(locale.value))
</script>

<template>
  <section class="cb-research-hero">
    <p class="cb-research-kicker">{{ content.eyebrow }}</p>
    <div class="cb-research-grid">
      <p class="cb-research-abstract">{{ content.abstract }}</p>
      <ul class="cb-research-theses">
        <li v-for="item in content.theses" :key="item">{{ item }}</li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.cb-research-hero {
  margin: 0 0 2.25rem;
  padding: 1.75rem 0 0;
}

.cb-research-kicker {
  margin: 0 0 0.8rem;
  color: var(--cb-accent);
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.cb-research-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 1.25rem 2rem;
  align-items: start;
}

.cb-research-abstract {
  margin: 0;
  color: var(--cb-text);
  font-size: clamp(1.05rem, 2vw, 1.35rem);
  line-height: 1.75;
  max-width: 36ch;
}

.cb-research-theses {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.75rem;
}

.cb-research-theses li {
  padding: 0.95rem 1rem;
  border: 1px solid var(--cb-border);
  border-radius: 16px;
  background: var(--cb-bg-elevated);
  color: var(--cb-text-2);
  line-height: 1.65;
}

@media (max-width: 760px) {
  .cb-research-grid {
    grid-template-columns: 1fr;
  }
}
</style>
