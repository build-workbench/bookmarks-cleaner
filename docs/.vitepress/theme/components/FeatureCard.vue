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
    class="feature-card"
    :class="{ clickable: link }"
    @click="navigate"
  >
    <div class="icon-wrapper">
      <span class="icon">{{ icon }}</span>
    </div>
    <h3 class="card-title">{{ title }}</h3>
    <p class="card-description">{{ description }}</p>
    <div v-if="link" class="card-link">
      <span>了解更多</span>
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M7 17L17 7M17 7H7M17 7V17"/>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.feature-card {
  padding: 24px;
  border-radius: 14px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-border);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--cb-gradient-hero);
  opacity: 0;
  transition: opacity 0.15s ease;
}

.feature-card.clickable {
  cursor: pointer;
}

.feature-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-4px);
  box-shadow: var(--cb-glow);
}

.feature-card:hover::before {
  opacity: 1;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  margin-bottom: 16px;
  background: var(--cb-gradient-card);
  border-radius: 10px;
}

.icon {
  font-size: 26px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--vp-c-text-1);
}

.card-description {
  font-size: 14px;
  line-height: 1.7;
  color: var(--vp-c-text-2);
  margin: 0;
}

.card-link {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-brand-1);
}

.card-link svg {
  transition: transform 0.2s ease;
}

.feature-card:hover .card-link svg {
  transform: translate(2px, -2px);
}

@media (max-width: 640px) {
  .feature-card {
    padding: 20px;
  }

  .icon-wrapper {
    width: 44px;
    height: 44px;
  }

  .icon {
    font-size: 22px;
  }
}
</style>
