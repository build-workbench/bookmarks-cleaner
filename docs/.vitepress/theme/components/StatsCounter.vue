<template>
  <div class="stats-counter">
    <div 
      v-for="(stat, index) in stats" 
      :key="index"
      class="stat-item"
      :class="{ 'is-visible': isVisible }"
      :style="{ animationDelay: `${index * 100}ms` }"
    >
      <div class="stat-icon" v-if="stat.icon">{{ stat.icon }}</div>
      <div class="stat-value">
        <span class="stat-number">{{ formatValue(animatedValues[index]) }}</span>
        <span v-if="stat.suffix" class="stat-suffix">{{ stat.suffix }}</span>
      </div>
      <div class="stat-label">{{ stat.label }}</div>
      <div v-if="stat.description" class="stat-description">{{ stat.description }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

interface Stat {
  value: number
  label: string
  icon?: string
  suffix?: string
  description?: string
  decimals?: number
  prefix?: string
}

interface Props {
  stats: Stat[]
  duration?: number
  triggerOnVisible?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  duration: 2000,
  triggerOnVisible: true
})

const isVisible = ref(false)
const animatedValues = ref<number[]>(props.stats.map(() => 0))
let animationFrame: number | null = null
let observer: IntersectionObserver | null = null

const containerRef = ref<HTMLElement | null>(null)

const formatValue = (value: number): string => {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'k'
  }
  return value.toFixed(0)
}

const animate = () => {
  const startTime = performance.now()
  const startValues = [...animatedValues.value]
  const targetValues = props.stats.map(s => s.value)
  
  const step = (currentTime: number) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / props.duration, 1)
    
    // Easing function (ease-out-cubic)
    const easeOut = 1 - Math.pow(1 - progress, 3)
    
    animatedValues.value = targetValues.map((target, i) => {
      return startValues[i] + (target - startValues[i]) * easeOut
    })
    
    if (progress < 1) {
      animationFrame = requestAnimationFrame(step)
    }
  }
  
  animationFrame = requestAnimationFrame(step)
}

const onIntersection = (entries: IntersectionObserverEntry[]) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !isVisible.value) {
      isVisible.value = true
      animate()
    }
  })
}

onMounted(() => {
  if (props.triggerOnVisible && typeof window !== 'undefined') {
    observer = new IntersectionObserver(onIntersection, {
      threshold: 0.3,
      rootMargin: '0px 0px -50px 0px'
    })
    
    // Find parent element
    const el = document.querySelector('.stats-counter')
    if (el) {
      observer.observe(el)
    }
  } else {
    isVisible.value = true
    animate()
  }
})

onUnmounted(() => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.stats-counter {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.stat-item {
  text-align: center;
  padding: 1.5rem;
  border-radius: var(--cb-radius-lg);
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(20px);
}

.stat-item.is-visible {
  animation: fadeInUp 0.6s ease forwards;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--cb-shadow-lg);
  border-color: var(--cb-brand);
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
  display: inline-block;
  animation: float 3s ease-in-out infinite;
}

.stat-value {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 0.25rem;
  line-height: 1;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--cb-brand) 0%, var(--cb-accent-purple) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-suffix {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--cb-brand);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--vp-c-text-2);
  margin-top: 0.5rem;
  font-weight: 500;
}

.stat-description {
  font-size: 0.75rem;
  color: var(--vp-c-text-3);
  margin-top: 0.25rem;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

@media (max-width: 640px) {
  .stats-counter {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-number {
    font-size: 2rem;
  }
}
</style>
