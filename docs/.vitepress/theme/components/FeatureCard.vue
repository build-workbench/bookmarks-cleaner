<template>
  <div 
    class="cb-feature-card"
    :class="{ 'is-interactive': interactive }"
    @mouseenter="onHover"
    @mouseleave="onLeave"
  >
    <div class="feature-icon-wrapper" :class="{ 'is-animated': isHovered && animated }">
      <span class="feature-icon">{{ icon }}</span>
    </div>
    <h3 class="feature-title">{{ title }}</h3>
    <p class="feature-description">{{ description }}</p>
    
    <div v-if="tags && tags.length" class="feature-tags">
      <span 
        v-for="tag in tags" 
        :key="tag"
        class="feature-tag"
      >{{ tag }}</span>
    </div>
    
    <div v-if="link" class="feature-link">
      <a :href="link">了解更多 →</a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  icon: string
  title: string
  description: string
  link?: string
  tags?: string[]
  interactive?: boolean
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  interactive: true,
  animated: true,
  link: '',
  tags: () => []
})

const isHovered = ref(false)

const onHover = () => {
  if (props.interactive) {
    isHovered.value = true
  }
}

const onLeave = () => {
  isHovered.value = false
}
</script>

<style scoped>
.cb-feature-card {
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  border-radius: var(--cb-radius-lg);
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  height: 100%;
}

.cb-feature-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(145deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.cb-feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.15);
  border-color: var(--cb-brand);
}

.cb-feature-card:hover::before {
  opacity: 1;
}

.feature-icon-wrapper {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--cb-brand) 0%, var(--cb-accent-purple) 100%);
  border-radius: var(--cb-radius);
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
  transition: transform 0.3s ease;
}

.feature-icon-wrapper.is-animated {
  animation: bounce 0.6s ease;
}

.feature-icon {
  font-size: 1.75rem;
  line-height: 1;
}

.feature-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 1;
}

.feature-description {
  color: var(--vp-c-text-2);
  line-height: 1.6;
  font-size: 0.9375rem;
  position: relative;
  z-index: 1;
  flex: 1;
}

.feature-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
  position: relative;
  z-index: 1;
}

.feature-tag {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  padding: 0.25rem 0.5rem;
  background: var(--vp-c-bg-soft);
  border-radius: var(--cb-radius-full);
  color: var(--vp-c-text-2);
}

.feature-link {
  margin-top: 1rem;
  position: relative;
  z-index: 1;
}

.feature-link a {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--cb-brand);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: gap 0.2s ease;
}

.feature-link a:hover {
  gap: 0.5rem;
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
</style>
