<script setup lang="ts">
import { useData } from 'vitepress'

const { isDark } = useData()

interface Stage {
  id: number
  name: string
  label: string
  desc: string
}

interface Classifier {
  name: string
  weight: number
  color: string
}

const stages: Stage[] = [
  { id: 1, name: 'BookmarkLoader', label: 'Loader', desc: 'Load & Parse' },
  { id: 2, name: 'Deduplicator', label: 'Deduplicate', desc: 'Remove Duplicates' },
  { id: 3, name: 'Classifier', label: 'Classify', desc: 'AI Classification' },
  { id: 4, name: 'Organizer', label: 'Organize', desc: 'Build Hierarchy' },
  { id: 5, name: 'Exporter', label: 'Export', desc: 'Multi-format Output' },
]

const classifiers: Classifier[] = [
  { name: 'RuleEngine', weight: 0.50, color: '#0066FF' },
  { name: 'MLClassifier', weight: 0.15, color: '#00C8A0' },
  { name: 'SemanticAnalyzer', weight: 0.10, color: '#7C3AED' },
  { name: 'LLMClassifier', weight: 0.50, color: '#F59E0B' },
]

function getStageColor(index: number): string {
  const colors = ['#0066FF', '#00A3FF', '#00C8A0', '#7C3AED', '#F59E0B']
  return colors[index % colors.length]
}
</script>

<template>
  <div class="cb-architecture">
    <!-- Pipeline Section -->
    <div class="cb-arch-section">
      <div class="cb-arch-label">Processing Pipeline</div>
      <div class="cb-pipeline">
        <div
          v-for="(stage, index) in stages"
          :key="stage.id"
          class="cb-pipeline-stage"
          :style="{ '--stage-color': getStageColor(index) }"
        >
          <div class="cb-stage-num">0{{ stage.id }}</div>
          <div class="cb-stage-name">{{ stage.name }}</div>
          <div class="cb-stage-desc">{{ stage.desc }}</div>
          <div v-if="index < stages.length - 1" class="cb-stage-arrow">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Fusion Section -->
    <div class="cb-arch-section">
      <div class="cb-arch-label">Classifier Fusion</div>
      <div class="cb-fusion">
        <div
          v-for="clf in classifiers"
          :key="clf.name"
          class="cb-fusion-item"
          :style="{ '--clf-color': clf.color }"
        >
          <div class="cb-fusion-header">
            <span class="cb-fusion-name">{{ clf.name }}</span>
            <span class="cb-fusion-weight">{{ (clf.weight * 100).toFixed(0) }}%</span>
          </div>
          <div class="cb-fusion-bar-bg">
            <div
              class="cb-fusion-bar-fill"
              :style="{ width: `${clf.weight * 100}%`, background: clf.color }"
            />
          </div>
        </div>
        <div class="cb-fusion-engine">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
          <span>FusionEngine</span>
          <span class="cb-fusion-badge">Weighted Vote</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cb-architecture {
  margin: 32px 0;
  padding: 28px;
  background: var(--cb-bg-soft);
  border-radius: 16px;
  border: 1px solid var(--cb-border);
}

.cb-arch-section {
  margin-bottom: 28px;
}

.cb-arch-section:last-child {
  margin-bottom: 0;
}

.cb-arch-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--cb-text-muted);
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--cb-border);
}

/* Pipeline */
.cb-pipeline {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex-wrap: wrap;
}

.cb-pipeline-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 20px;
  background: var(--cb-bg);
  border-radius: 12px;
  border: 1px solid var(--cb-border);
  min-width: 120px;
  position: relative;
  transition: all var(--cb-motion-normal);
}

.cb-pipeline-stage:hover {
  border-color: var(--stage-color);
  box-shadow: 0 0 20px color-mix(in srgb, var(--stage-color) 15%, transparent);
  transform: translateY(-2px);
}

.cb-stage-num {
  font-size: 12px;
  font-weight: 700;
  color: var(--stage-color);
  margin-bottom: 8px;
  font-family: var(--cb-font-mono);
}

.cb-stage-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--cb-text);
  font-family: var(--cb-font-mono);
  margin-bottom: 4px;
}

.cb-stage-desc {
  font-size: 11px;
  color: var(--cb-text-3);
}

.cb-stage-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--cb-brand);
  opacity: 0.5;
}

/* Fusion */
.cb-fusion {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.cb-fusion-item {
  padding: 14px 16px;
  background: var(--cb-bg);
  border-radius: 10px;
  border: 1px solid var(--cb-border);
  transition: border-color var(--cb-motion-fast);
}

.cb-fusion-item:hover {
  border-color: var(--clf-color);
}

.cb-fusion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.cb-fusion-name {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--cb-text);
  font-family: var(--cb-font-mono);
}

.cb-fusion-weight {
  font-size: 12px;
  font-weight: 700;
  color: var(--clf-color);
  font-family: var(--cb-font-mono);
}

.cb-fusion-bar-bg {
  height: 4px;
  background: var(--cb-bg-soft);
  border-radius: 2px;
  overflow: hidden;
}

.cb-fusion-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.cb-fusion-engine {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: var(--cb-brand-soft);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--cb-brand);
  border: 1px solid var(--cb-brand-soft);
}

.cb-fusion-badge {
  margin-left: auto;
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 6px;
  background: var(--cb-bg);
  color: var(--cb-brand);
  font-weight: 500;
}

@media (max-width: 640px) {
  .cb-pipeline {
    flex-direction: column;
    align-items: stretch;
  }

  .cb-pipeline-stage {
    flex-direction: row;
    align-items: center;
    gap: 12px;
    min-width: auto;
  }

  .cb-stage-num {
    margin-bottom: 0;
  }

  .cb-stage-arrow {
    transform: rotate(90deg);
    align-self: center;
  }

  .cb-fusion {
    grid-template-columns: 1fr;
  }
}
</style>
