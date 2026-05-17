<script setup lang="ts">
const props = withDefaults(defineProps<{
  icon: string
  title: string
  description: string
  link?: string
}>(), {
  link: ''
})

function navigate() {
  if (props.link) {
    window.location.href = props.link
  }
}
</script>

<template>
  <div
    class="cb-feature-card"
    :class="{ 'cb-clickable': link }"
    @click="navigate"
  >
    <div class="cb-card-icon-wrapper">
      <span class="cb-card-icon" v-html="icon"></span>
    </div>
    <h3 class="cb-card-title">{{ title }}</h3>
    <p class="cb-card-description">{{ description }}</p>
    <div v-if="link" class="cb-card-link">
      <span>了解更多</span>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M7 17L17 7M17 7H7M17 7V17"/>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.cb-feature-card {
  padding: 28px;
  border-radius: 16px;
  background: var(--cb-bg);
  border: 1px solid var(--cb-border);
  transition: all var(--cb-motion-normal);
  position: relative;
  overflow: hidden;
}

.cb-feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--cb-grad-brand);
  opacity: 0;
  transition: opacity var(--cb-motion-fast);
}

.cb-feature-card.cb-clickable {
  cursor: pointer;
}

.cb-feature-card:hover {
  border-color: var(--cb-brand);
  transform: translateY(-4px);
  box-shadow: var(--cb-shadow-lg);
}

.cb-feature-card:hover::before {
  opacity: 1;
}

.cb-card-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  margin-bottom: 18px;
  background: var(--cb-grad-card);
  border: 1px solid var(--cb-border);
  border-radius: 12px;
  transition: all var(--cb-motion-normal);
}

.cb-feature-card:hover .cb-card-icon-wrapper {
  background: var(--cb-brand-soft);
  transform: scale(1.05);
  border-color: var(--cb-brand);
}

.cb-card-icon {
  color: var(--cb-brand);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cb-card-icon :deep(svg) {
  width: 24px;
  height: 24px;
}

.cb-card-title {
  font-size: 17px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--cb-text);
  letter-spacing: -0.2px;
}

.cb-card-description {
  font-size: 14px;
  line-height: 1.7;
  color: var(--cb-text-3);
  margin: 0;
}

.cb-card-link {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--cb-brand);
}

.cb-card-link svg {
  transition: transform var(--cb-motion-fast);
}

.cb-feature-card:hover .cb-card-link svg {
  transform: translate(2px, -2px);
}

@media (max-width: 640px) {
  .cb-feature-card {
    padding: 22px;
  }

  .cb-card-icon-wrapper {
    width: 44px;
    height: 44px;
  }

  .cb-card-icon :deep(svg) {
    width: 20px;
    height: 20px;
  }
}
</style>
