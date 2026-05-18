<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'
import { getLandingContent } from '../home-content.mjs'

const { lang } = useData()
const locale = computed(() => lang.value === 'zh-CN' ? 'zh' : 'en')
const content = computed(() => getLandingContent(locale.value))
</script>

<template>
  <section class="cb-citation-cluster">
    <header class="cb-citation-header">
      <h2>{{ locale === 'zh' ? '进一步阅读' : 'Further reading' }}</h2>
      <p>
        {{
          locale === 'zh'
            ? '把论文、相关项目和演进记录放到同一阅读出口，形成完整证据链。'
            : 'Keep the literature, competitor analysis, and evolution notes in the same evidence trail.'
        }}
      </p>
    </header>

    <div class="cb-citation-grid">
      <a
        v-for="item in content.citations"
        :key="item.title"
        class="cb-citation-card"
        :href="item.href"
      >
        <strong>{{ item.title }}</strong>
        <span>{{ item.detail }}</span>
      </a>
    </div>
  </section>
</template>

<style scoped>
.cb-citation-cluster {
  margin: 2.75rem 0 1rem;
  padding: 1.5rem 0 0;
  border-top: 1px solid var(--cb-border);
}

.cb-citation-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.cb-citation-header h2,
.cb-citation-header p {
  margin: 0;
}

.cb-citation-header p {
  max-width: 45ch;
  color: var(--cb-text-3);
}

.cb-citation-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.cb-citation-card {
  display: grid;
  gap: 0.45rem;
  padding: 1rem 1.1rem;
  border-radius: 18px;
  border: 1px solid var(--cb-border);
  background: var(--cb-bg-elevated);
  box-shadow: var(--cb-shadow-sm);
}

.cb-citation-card strong {
  color: var(--cb-text);
}

.cb-citation-card span {
  color: var(--cb-text-3);
  line-height: 1.6;
}

@media (max-width: 760px) {
  .cb-citation-grid {
    grid-template-columns: 1fr;
  }
}
</style>
