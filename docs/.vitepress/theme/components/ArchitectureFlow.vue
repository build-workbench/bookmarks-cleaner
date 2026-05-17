<script setup lang="ts">
// ArchitectureFlow - Pipeline 流程可视化组件
// 用于展示书签处理的 5 阶段 Pipeline 架构

const stages = [
  { id: 1, name: 'BookmarkLoader', icon: '📥', desc: '加载书签文件' },
  { id: 2, name: 'Deduplication', icon: '🔄', desc: '去重处理' },
  { id: 3, name: 'Classification', icon: '🏷️', desc: '智能分类' },
  { id: 4, name: 'Organization', icon: '📁', desc: '组织整理' },
  { id: 5, name: 'Export', icon: '📤', desc: '导出输出' },
]

const classifiers = [
  { name: 'RuleEngine', weight: 0.35 },
  { name: 'MLClassifier', weight: 0.25 },
  { name: 'SemanticAnalyzer', weight: 0.20 },
  { name: 'LLMClassifier', weight: 0.20 },
]
</script>

<template>
  <div class="architecture-flow">
    <div class="pipeline-section">
      <h4 class="section-title">处理管道</h4>
      <div class="pipeline-stages">
        <template v-for="(stage, index) in stages" :key="stage.id">
          <div class="stage">
            <div class="stage-icon">{{ stage.icon }}</div>
            <div class="stage-info">
              <span class="stage-name">{{ stage.name }}</span>
              <span class="stage-desc">{{ stage.desc }}</span>
            </div>
          </div>
          <div v-if="index < stages.length - 1" class="arrow">→</div>
        </template>
      </div>
    </div>

    <div class="classifier-section">
      <h4 class="section-title">分类器融合</h4>
      <div class="classifier-grid">
        <div v-for="clf in classifiers" :key="clf.name" class="classifier">
          <span class="clf-name">{{ clf.name }}</span>
          <div class="clf-weight">
            <div class="weight-bar" :style="{ width: `${clf.weight * 100}%` }"></div>
            <span class="weight-text">{{ (clf.weight * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>
      <div class="fusion-result">
        <span class="fusion-icon">⚡</span>
        <span>FusionEngine 加权融合</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.architecture-flow {
  margin: 32px 0;
  padding: 24px;
  background: var(--vp-c-bg-soft);
  border-radius: 14px;
  border: 1px solid var(--vp-c-border);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 16px;
}

.pipeline-section {
  margin-bottom: 32px;
}

.pipeline-stages {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.stage {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--vp-c-bg);
  border-radius: 10px;
  border: 1px solid var(--vp-c-border);
  transition: all 0.2s ease;
}

.stage:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 0 20px rgba(0, 102, 255, 0.1);
}

.stage-icon {
  font-size: 20px;
}

.stage-info {
  display: flex;
  flex-direction: column;
}

.stage-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--vp-c-text-1);
  font-family: var(--vp-font-family-mono);
}

.stage-desc {
  font-size: 11px;
  color: var(--vp-c-text-3);
}

.arrow {
  font-size: 20px;
  color: var(--vp-c-brand-1);
  font-weight: 300;
}

.classifier-section {
  padding-top: 24px;
  border-top: 1px solid var(--vp-c-border);
}

.classifier-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.classifier {
  padding: 12px 16px;
  background: var(--vp-c-bg);
  border-radius: 8px;
  border: 1px solid var(--vp-c-border);
}

.clf-name {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--vp-c-text-1);
  margin-bottom: 8px;
  font-family: var(--vp-font-family-mono);
}

.clf-weight {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weight-bar {
  height: 4px;
  background: var(--cb-gradient-hero);
  border-radius: 2px;
}

.weight-text {
  font-size: 12px;
  color: var(--vp-c-text-3);
  font-family: var(--vp-font-family-mono);
}

.fusion-result {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--vp-c-brand-soft);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-brand-1);
}

.fusion-icon {
  font-size: 18px;
}

@media (max-width: 640px) {
  .pipeline-stages {
    flex-direction: column;
    align-items: stretch;
  }

  .arrow {
    transform: rotate(90deg);
    align-self: center;
  }

  .classifier-grid {
    grid-template-columns: 1fr;
  }
}
</style>
