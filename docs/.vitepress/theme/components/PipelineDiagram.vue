<template>
  <div class="pipeline-diagram" :class="`layout-${layout}`">
    <div class="pipeline-container">
      <div 
        v-for="(step, index) in steps" 
        :key="index"
        class="pipeline-step"
        :class="{ 
          'is-active': activeStep === index,
          'is-completed': completedSteps.includes(index),
          'is-interactive': interactive
        }"
        :style="{ animationDelay: `${index * 150}ms` }"
        @click="interactive && selectStep(index)"
        @mouseenter="interactive && hoverStep(index)"
      >
        <div class="step-connector" v-if="index > 0">
          <span class="connector-line"></span>
          <span class="connector-arrow">→</span>
        </div>
        
        <div class="step-content">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-icon" v-if="step.icon">{{ step.icon }}</div>
          <div class="step-badge" v-else>{{ step.badge || index + 1 }}</div>
          
          <div class="step-info">
            <h4 class="step-title">{{ step.title }}</h4>
            <p class="step-description">{{ step.description }}</p>
            <div v-if="step.meta" class="step-meta">
              <span v-for="(meta, idx) in step.meta" :key="idx" class="meta-item">
                {{ meta }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="interactive && selectedStep !== null" class="pipeline-detail">
      <div class="detail-content">
        <h5>{{ steps[selectedStep].title }} - 详细信息</h5>
        <p>{{ steps[selectedStep].detail || steps[selectedStep].description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Step {
  title: string
  description: string
  detail?: string
  icon?: string
  badge?: string
  meta?: string[]
}

interface Props {
  steps: Step[]
  layout?: 'vertical' | 'horizontal'
  interactive?: boolean
  autoPlay?: boolean
  autoPlayInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'vertical',
  interactive: true,
  autoPlay: false,
  autoPlayInterval: 2000
})

const activeStep = ref<number | null>(null)
const selectedStep = ref<number | null>(null)
const completedSteps = ref<number[]>([])

const selectStep = (index: number) => {
  selectedStep.value = index
  if (!completedSteps.value.includes(index)) {
    completedSteps.value.push(index)
  }
}

const hoverStep = (index: number) => {
  activeStep.value = index
}

// Auto-play functionality
if (props.autoPlay) {
  let currentIndex = 0
  setInterval(() => {
    activeStep.value = currentIndex
    if (!completedSteps.value.includes(currentIndex)) {
      completedSteps.value.push(currentIndex)
    }
    currentIndex = (currentIndex + 1) % props.steps.length
  }, props.autoPlayInterval)
}
</script>

<style scoped>
.pipeline-diagram {
  margin: 2rem 0;
}

.pipeline-container {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.layout-horizontal .pipeline-container {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 1rem;
}

.pipeline-step {
  position: relative;
  padding: 1rem 0;
  opacity: 0;
  animation: fadeInSlide 0.5s ease forwards;
}

.pipeline-step.is-interactive {
  cursor: pointer;
}

@keyframes fadeInSlide {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.step-connector {
  position: absolute;
  left: 24px;
  top: -1rem;
  bottom: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--vp-c-divider);
}

.step-connector .connector-line {
  flex: 1;
  width: 2px;
  background: var(--vp-c-divider);
}

.step-connector .connector-arrow {
  font-size: 0.875rem;
  margin-top: -0.25rem;
}

.layout-horizontal .step-connector {
  display: none;
}

.step-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--cb-radius);
  transition: all 0.3s ease;
}

.step-content:hover,
.pipeline-step.is-active .step-content {
  border-color: var(--cb-brand);
  box-shadow: var(--cb-shadow-md);
  background: var(--vp-c-bg-soft);
}

.pipeline-step.is-completed .step-content {
  border-color: var(--cb-accent-green);
}

.step-number {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cb-gradient-primary);
  color: white;
  font-weight: 700;
  font-size: 0.875rem;
  border-radius: 50%;
  z-index: 1;
}

.step-icon {
  font-size: 1.5rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--vp-c-brand-soft);
  border-radius: var(--cb-radius);
}

.step-badge {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--vp-c-brand-soft);
  border-radius: var(--cb-radius);
  font-weight: 700;
  color: var(--cb-brand);
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.step-description {
  font-size: 0.875rem;
  color: var(--vp-c-text-2);
  line-height: 1.5;
}

.step-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.meta-item {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  padding: 0.25rem 0.5rem;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--cb-radius-full);
  color: var(--vp-c-text-2);
}

.pipeline-step.is-active .meta-item {
  background: var(--vp-c-brand-soft);
  border-color: var(--cb-brand);
  color: var(--cb-brand);
}

.pipeline-detail {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background: var(--vp-c-bg-soft);
  border-radius: var(--cb-radius);
  border-left: 3px solid var(--cb-brand);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.detail-content h5 {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.detail-content p {
  color: var(--vp-c-text-2);
  font-size: 0.9375rem;
  line-height: 1.6;
}

/* Horizontal layout variants */
.layout-horizontal .pipeline-step {
  flex: 1;
  min-width: 200px;
}

.layout-horizontal .step-content {
  flex-direction: column;
  text-align: center;
}

.layout-horizontal .step-number {
  position: static;
  transform: none;
  margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
  .layout-horizontal .pipeline-container {
    flex-direction: column;
  }
  
  .step-content {
    padding-left: 3rem;
  }
  
  .step-number {
    left: 1.25rem;
  }
}
</style>
