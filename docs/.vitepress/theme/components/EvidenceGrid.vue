<script setup lang="ts">
import { computed } from 'vue'
import { getLandingContent } from '../home-content.mjs'

const content = computed(() => getLandingContent())
</script>

<template>
  <section class="cb-evidence-grid">
    <article
      v-for="(item, index) in content.evidence"
      :key="item.title"
      :class="['cb-evidence-card', { 'cb-evidence-featured': index === 0 }]"
    >
      <h3>{{ item.title }}</h3>
      <p>{{ item.detail }}</p>
      <a :href="item.href">继续阅读</a>
    </article>
  </section>
</template>

<style scoped>
.cb-evidence-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 1rem;
  margin: 2.5rem 0;
}

.cb-evidence-card {
  grid-column: span 4;
  padding: 1.3rem;
  border-radius: 20px;
  border: 1px solid var(--cb-border);
  background: var(--cb-bg-elevated);
  box-shadow: var(--cb-shadow-sm);
}

.cb-evidence-featured {
  grid-column: span 6;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--cb-accent) 7%, transparent), transparent 65%),
    var(--cb-bg-elevated);
}

.cb-evidence-card h3,
.cb-evidence-card p {
  margin: 0;
}

.cb-evidence-card h3 {
  color: var(--cb-text);
  font-size: 1.05rem;
}

.cb-evidence-card p {
  margin-top: 0.75rem;
  color: var(--cb-text-2);
  line-height: 1.7;
}

.cb-evidence-card a {
  display: inline-flex;
  margin-top: 1rem;
  color: var(--cb-accent);
  font-weight: 700;
}

@media (max-width: 960px) {
  .cb-evidence-card,
  .cb-evidence-featured {
    grid-column: span 6;
  }
}

@media (max-width: 640px) {
  .cb-evidence-card,
  .cb-evidence-featured {
    grid-column: 1 / -1;
  }
}
</style>
