<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useData } from 'vitepress'

const { lang, isDark } = useData()
const isZh = computed(() => lang.value === 'zh-CN')

const chartRef = ref<HTMLElement | null>(null)
const hasAnimated = ref(false)
const animationProgress = ref(0)

let animFrame = 0
let observer: IntersectionObserver | null = null

function animateIn() {
  if (hasAnimated.value) return
  hasAnimated.value = true
  const start = performance.now()
  const duration = 900

  function tick(now: number) {
    const elapsed = now - start
    animationProgress.value = Math.min(elapsed / duration, 1)
    if (animationProgress.value < 1) {
      animFrame = requestAnimationFrame(tick)
    }
  }
  animFrame = requestAnimationFrame(tick)
}

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => { if (entries[0]?.isIntersecting) animateIn() },
    { threshold: 0.25 }
  )
  if (chartRef.value) observer.observe(chartRef.value)
})

onUnmounted(() => {
  observer?.disconnect()
  cancelAnimationFrame(animFrame)
})

// Ease out cubic
function easeOut(t: number) {
  return 1 - (1 - t) ** 3
}

function barWidth(target: number) {
  return `${easeOut(animationProgress.value) * target}%`
}

const labels = computed(() => isZh.value ? {
  title: '性能基准对比',
  subtitle: '三种运行模式下的相对吞吐率（规则模式 = 100%）',
  modes: ['仅规则模式', '规则 + ML 混合', '规则 + ML + LLM'],
  note: '基准测试环境：Ryzen 5 5600X，1,000 书签测试集，单线程运行',
  labels: ['0', '25%', '50%', '75%', '100%'],
} : {
  title: 'Performance Benchmark',
  subtitle: 'Relative throughput across three runtime modes (rules-only = 100%)',
  modes: ['Rules only', 'Rules + ML hybrid', 'Rules + ML + LLM'],
  note: 'Benchmark: Ryzen 5 5600X, 1,000-bookmark test set, single-threaded',
  labels: ['0', '25%', '50%', '75%', '100%'],
})

// Bar data: [targetWidth%, throughput, latency label]
const bars = computed(() => [
  { pct: 100, value: '620/s', tag: isZh.value ? '最快 · 零延迟启动' : 'Fastest · zero cold-start', color: 'accent' },
  { pct: 58,  value: '360/s', tag: isZh.value ? '均衡 · ML 依赖冷启动' : 'Balanced · ML cold-start cost', color: 'support' },
  { pct: 12,  value: '75/s',  tag: isZh.value ? '最强 · 网络延迟主导' : 'Strongest · network-latency bound', color: 'highlight' },
])
</script>

<template>
  <section ref="chartRef" class="cb-perf-chart">
    <header class="cb-perf-header">
      <h3>{{ labels.title }}</h3>
      <p>{{ labels.subtitle }}</p>
    </header>

    <div class="cb-perf-body">
      <!-- Y-axis grid lines -->
      <div class="cb-perf-grid" aria-hidden="true">
        <div v-for="l in labels.labels" :key="l" class="cb-perf-grid-col">
          <span>{{ l }}</span>
        </div>
      </div>

      <!-- Bars -->
      <ol class="cb-perf-bars">
        <li
          v-for="(bar, idx) in bars"
          :key="idx"
          class="cb-perf-row"
        >
          <span class="cb-perf-mode">{{ labels.modes[idx] }}</span>
          <div class="cb-perf-track">
            <div
              class="cb-perf-bar"
              :class="`cb-bar-${bar.color}`"
              :style="{ width: barWidth(bar.pct) }"
            >
              <span class="cb-perf-bar-value">{{ bar.value }}</span>
            </div>
          </div>
          <span class="cb-perf-tag">{{ bar.tag }}</span>
        </li>
      </ol>
    </div>

    <p class="cb-perf-note">{{ labels.note }}</p>
  </section>
</template>

<style scoped>
.cb-perf-chart {
  margin: 2.25rem 0;
  padding: 1.5rem;
  border: 1px solid var(--cb-border);
  border-radius: var(--cb-radius-xl);
  background: var(--cb-bg-elevated);
  box-shadow: var(--cb-shadow-sm);
}

.cb-perf-header {
  margin-bottom: 1.5rem;
}

.cb-perf-header h3,
.cb-perf-header p {
  margin: 0;
}

.cb-perf-header h3 {
  color: var(--cb-text);
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.025em;
}

.cb-perf-header p {
  margin-top: 0.3rem;
  color: var(--cb-text-3);
  font-size: 0.88rem;
}

.cb-perf-body {
  position: relative;
}

/* Grid lines */
.cb-perf-grid {
  position: absolute;
  inset: 0;
  display: flex;
  pointer-events: none;
}

.cb-perf-grid-col {
  flex: 1;
  border-left: 1px dashed var(--cb-border);
  display: flex;
  align-items: flex-end;
  padding-bottom: 0.2rem;
}

.cb-perf-grid-col:first-child {
  border-left: none;
}

.cb-perf-grid-col span {
  font-family: var(--cb-font-mono);
  font-size: 0.68rem;
  color: var(--cb-text-muted);
  padding-left: 0.35rem;
}

/* Bars */
.cb-perf-bars {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 1rem;
  position: relative;
  z-index: 1;
}

.cb-perf-row {
  display: grid;
  grid-template-columns: 160px 1fr 200px;
  gap: 0.75rem;
  align-items: center;
}

.cb-perf-mode {
  color: var(--cb-text-2);
  font-size: 0.88rem;
  font-weight: 700;
  font-family: var(--cb-font-mono);
  text-align: right;
  white-space: nowrap;
}

.cb-perf-track {
  height: 2.25rem;
  background: var(--cb-bg-soft);
  border-radius: var(--cb-radius-sm);
  overflow: hidden;
  border: 1px solid var(--cb-border);
}

.cb-perf-bar {
  height: 100%;
  border-radius: var(--cb-radius-sm);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 0.75rem;
  min-width: 3rem;
  transition: width 0.05s linear;
}

.cb-bar-accent {
  background: linear-gradient(90deg,
    color-mix(in srgb, var(--cb-accent) 40%, transparent),
    var(--cb-accent));
}

.cb-bar-support {
  background: linear-gradient(90deg,
    color-mix(in srgb, var(--cb-support) 40%, transparent),
    var(--cb-support));
}

.cb-bar-highlight {
  background: linear-gradient(90deg,
    color-mix(in srgb, var(--cb-highlight) 40%, transparent),
    var(--cb-highlight));
}

.cb-perf-bar-value {
  color: #fff;
  font-family: var(--cb-font-mono);
  font-weight: 800;
  font-size: 0.82rem;
  white-space: nowrap;
  mix-blend-mode: plus-lighter;
}

.cb-perf-tag {
  color: var(--cb-text-3);
  font-size: 0.82rem;
  line-height: 1.4;
}

.cb-perf-note {
  margin: 1.25rem 0 0;
  color: var(--cb-text-muted);
  font-size: 0.8rem;
  font-family: var(--cb-font-mono);
  border-top: 1px solid var(--cb-border);
  padding-top: 0.75rem;
}

@media (max-width: 800px) {
  .cb-perf-row {
    grid-template-columns: 1fr;
    gap: 0.4rem;
  }

  .cb-perf-mode {
    text-align: left;
  }

  .cb-perf-tag {
    padding-left: 0;
  }

  .cb-perf-grid {
    display: none;
  }
}
</style>
