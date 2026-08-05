<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { getLandingContent } from '../home-content.mjs'

const content = computed(() => getLandingContent())

// Animated number counters via IntersectionObserver
const stripRef = ref<HTMLElement | null>(null)
const hasAnimated = ref(false)
const animatedValues = ref<string[]>([])

function initValues() {
  animatedValues.value = content.value.metrics.map(() => '—')
}

function animateIn() {
  if (hasAnimated.value) return
  hasAnimated.value = true
  content.value.metrics.forEach((item, idx) => {
    // Parse numeric prefix from value strings like "420-650/s", "<100 ms"
    setTimeout(() => {
      animatedValues.value[idx] = item.value
    }, idx * 120)
  })
}

let observer: IntersectionObserver | null = null

onMounted(() => {
  initValues()
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0]?.isIntersecting) animateIn()
    },
    { threshold: 0.3 }
  )
  if (stripRef.value) observer.observe(stripRef.value)
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <section ref="stripRef" class="cb-benchmark-strip" aria-label="Key metrics">
    <article
      v-for="(item, idx) in content.metrics"
      :key="item.label"
      class="cb-benchmark-item"
    >
      <p class="cb-benchmark-label">{{ item.label }}</p>
      <p class="cb-benchmark-value" :class="{ 'cb-value-loaded': hasAnimated }">
        {{ animatedValues[idx] ?? item.value }}
      </p>
      <p class="cb-benchmark-note">{{ item.note }}</p>
    </article>
  </section>
</template>

<style scoped>
.cb-benchmark-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.85rem;
  margin: 1.75rem 0 2.25rem;
}

.cb-benchmark-item {
  padding: 1.1rem 1.25rem;
  border-radius: var(--cb-radius-lg);
  border: 1px solid var(--cb-border);
  background: var(--cb-bg-elevated);
  box-shadow: var(--cb-shadow-sm);
  transition: border-color var(--cb-motion-normal), box-shadow var(--cb-motion-normal),
              transform var(--cb-motion-normal);
  cursor: default;
}

.cb-benchmark-item:hover {
  border-color: var(--cb-border-accent);
  box-shadow: var(--cb-shadow-accent);
  transform: translateY(-2px);
}

.cb-benchmark-label,
.cb-benchmark-value,
.cb-benchmark-note {
  margin: 0;
}

.cb-benchmark-label {
  color: var(--cb-text-muted);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-family: var(--cb-font-mono);
}

.cb-benchmark-value {
  margin-top: 0.6rem;
  color: var(--cb-text);
  font-size: 1.4rem;
  font-weight: 900;
  letter-spacing: -0.04em;
  font-family: var(--cb-font-mono);
  opacity: 0.4;
  transform: translateY(4px);
  transition: opacity 0.5s var(--cb-ease-spring), transform 0.5s var(--cb-ease-spring);
}

.cb-benchmark-value.cb-value-loaded {
  opacity: 1;
  transform: translateY(0);
  color: var(--cb-accent);
}

.cb-benchmark-note {
  margin-top: 0.55rem;
  color: var(--cb-text-3);
  font-size: 0.85rem;
  line-height: 1.55;
}

@media (max-width: 960px) {
  .cb-benchmark-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .cb-benchmark-strip {
    grid-template-columns: 1fr;
  }
}
</style>
