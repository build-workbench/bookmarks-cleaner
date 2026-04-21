<template>
  <div class="project-structure">
    <div class="structure-card">
      <div class="card-header">
        <span class="header-icon">📁</span>
        <span class="header-title">{{ title }}</span>
      </div>
      <div class="structure-tree">
        <div v-for="(item, index) in structure" :key="index" class="tree-item" :class="{ 'is-folder': item.type === 'folder' }">
          <span class="item-icon">{{ item.type === 'folder' ? '📂' : '📄' }}</span>
          <span class="item-name">{{ item.name }}</span>
          <span v-if="item.desc" class="item-desc">— {{ item.desc }}</span>
          <div v-if="item.children" class="tree-children">
            <div v-for="(child, cidx) in item.children" :key="cidx" class="tree-child">
              <span class="child-icon">{{ child.type === 'folder' ? '📁' : '📑' }}</span>
              <span class="child-name">{{ child.name }}</span>
              <span v-if="child.desc" class="child-desc">{{ child.desc }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '项目结构'
  },
  structure: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.project-structure {
  margin: 2rem 0;
}

.structure-card {
  background: var(--vp-c-bg-soft);
  border-radius: 12px;
  border: 1px solid var(--vp-c-divider);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  background: var(--vp-c-brand-soft);
  border-bottom: 1px solid var(--vp-c-divider);
}

.header-icon {
  font-size: 1.25rem;
}

.header-title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--vp-c-text-1);
}

.structure-tree {
  padding: 1rem 1.25rem;
  font-family: var(--vp-font-family-mono);
  font-size: 0.875rem;
}

.tree-item {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.375rem 0;
  color: var(--vp-c-text-2);
}

.tree-item.is-folder {
  color: var(--vp-c-text-1);
  font-weight: 500;
}

.item-icon, .child-icon {
  flex-shrink: 0;
}

.item-name, .child-name {
  font-family: var(--vp-font-family-mono);
}

.item-desc, .child-desc {
  color: var(--vp-c-text-3);
  font-size: 0.8rem;
  font-family: var(--vp-font-family-base);
}

.tree-children {
  width: 100%;
  margin-left: 1.5rem;
  margin-top: 0.25rem;
  padding-left: 1rem;
  border-left: 1px solid var(--vp-c-divider);
}

.tree-child {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  padding: 0.25rem 0;
  color: var(--vp-c-text-3);
}

.child-name {
  color: var(--vp-c-text-2);
}

@media (max-width: 640px) {
  .structure-tree {
    font-size: 0.8rem;
    padding: 0.75rem;
  }

  .tree-children {
    margin-left: 0.75rem;
    padding-left: 0.5rem;
  }
}
</style>
