<script setup lang="ts">
// A more dramatic pipeline visualization for whitepaper & architecture pages
const props = defineProps<{
  compact?: boolean
}>()

interface Step {
  label: string
  detail: string
  icon: string
}

const steps: Step[] = [
  { label: 'Parse', detail: 'HTML/JSON', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>' },
  { label: 'Deduplicate', detail: 'Hash & Sim', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12.01"/></svg>' },
  { label: 'Classify', detail: 'Rules + ML', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>' },
  { label: 'Organize', detail: 'Build Tree', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>' },
  { label: 'Export', detail: 'HTML/JSON/MD', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>' },
]
</script>

<template>
  <div class="cb-pipeline-viz" :class="{ 'cb-compact': compact }">
    <div class="cb-pipeline-track">
      <div
        v-for="(step, i) in steps"
        :key="step.label"
        class="cb-pipeline-step"
        :style="{ animationDelay: `${i * 0.15}s` }"
      >
        <div class="cb-step-icon" v-html="step.icon"></div>
        <div class="cb-step-label">{{ step.label }}</div>
        <div class="cb-step-detail">{{ step.detail }}</div>
        <div v-if="i < steps.length - 1" class="cb-step-connector"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cb-pipeline-viz {
  margin: 32px 0;
  padding: 28px;
  background: var(--cb-bg-soft);
  border-radius: 16px;
  border: 1px solid var(--cb-border);
  overflow-x: auto;
}

.cb-pipeline-track {
  display: flex;
  align-items: center;
  gap: 0;
  min-width: max-content;
}

.cb-pipeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  padding: 0 16px;
  opacity: 0;
  animation: cb-step-in 0.5s ease-out forwards;
}

@keyframes cb-step-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.cb-step-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cb-bg);
  border: 1.5px solid var(--cb-border);
  border-radius: 12px;
  color: var(--cb-brand);
  margin-bottom: 10px;
  transition: all var(--cb-motion-normal);
}

.cb-pipeline-step:hover .cb-step-icon {
  background: var(--cb-brand-soft);
  border-color: var(--cb-brand);
  transform: scale(1.08);
  box-shadow: var(--cb-glow);
}

.cb-step-icon :deep(svg) {
  width: 20px;
  height: 20px;
  stroke-width: 2;
}

.cb-step-label {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--cb-text);
  font-family: var(--cb-font-mono);
  margin-bottom: 2px;
}

.cb-step-detail {
  font-size: 11px;
  color: var(--cb-text-3);
}

.cb-step-connector {
  position: absolute;
  top: 22px;
  right: -12px;
  width: 24px;
  height: 2px;
  background: var(--cb-border);
}

.cb-step-connector::after {
  content: '';
  position: absolute;
  right: 0;
  top: -3px;
  width: 0;
  height: 0;
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
  border-left: 5px solid var(--cb-border);
}

.cb-compact {
  padding: 18px;
}

.cb-compact .cb-step-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
}

.cb-compact .cb-step-icon :deep(svg) {
  width: 16px;
  height: 16px;
}

.cb-compact .cb-step-connector {
  top: 18px;
  width: 18px;
}

@media (max-width: 640px) {
  .cb-pipeline-track {
    flex-direction: column;
    gap: 16px;
  }

  .cb-pipeline-step {
    flex-direction: row;
    gap: 14px;
    align-items: center;
    padding: 0;
    width: 100%;
  }

  .cb-step-icon {
    margin-bottom: 0;
  }

  .cb-step-connector {
    display: none;
  }
}
</style>
