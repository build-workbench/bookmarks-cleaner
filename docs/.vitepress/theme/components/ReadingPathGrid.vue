<script setup lang="ts">
import { computed } from 'vue'
import { getLandingContent } from '../home-content.mjs'

const content = computed(() => getLandingContent())
</script>

<template>
  <section class="cb-path-grid">
    <article v-for="item in content.paths" :key="item.index" class="cb-path-row">
      <div class="cb-path-index">{{ item.index }}</div>
      <div class="cb-path-body">
        <h3>{{ item.title }}</h3>
        <p>{{ item.detail }}</p>
      </div>
      <a class="cb-path-link" :href="item.href">进入</a>
    </article>
  </section>
</template>

<style scoped>
.cb-path-grid {
  margin: 2.75rem 0;
  border-top: 1px solid var(--cb-border);
}

.cb-path-row {
  display: grid;
  grid-template-columns: 84px minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1.1rem 0;
  border-bottom: 1px solid var(--cb-border);
}

.cb-path-index {
  color: var(--cb-text-muted);
  font-family: var(--cb-font-mono);
  font-weight: 700;
  font-size: 0.95rem;
}

.cb-path-body h3,
.cb-path-body p {
  margin: 0;
}

.cb-path-body h3 {
  color: var(--cb-text);
  font-size: 1rem;
}

.cb-path-body p {
  margin-top: 0.35rem;
  color: var(--cb-text-3);
  line-height: 1.6;
}

.cb-path-link {
  color: var(--cb-accent);
  font-weight: 700;
  white-space: nowrap;
}

@media (max-width: 640px) {
  .cb-path-row {
    grid-template-columns: 64px 1fr;
  }

  .cb-path-link {
    grid-column: 2;
  }
}
</style>
