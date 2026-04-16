<template>
  <div class="code-group">
    <div class="code-group-tabs" v-if="tabs.length > 1">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="code-group-tab"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <span v-if="tab.icon" class="tab-icon">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>
    <div class="code-group-content">
      <div
        v-for="tab in tabs"
        :key="tab.id"
        class="code-group-panel"
        :class="{ active: activeTab === tab.id }"
      >
        <div class="code-header" v-if="tab.filename">
          <span class="code-filename">{{ tab.filename }}</span>
          <button class="code-copy" @click="copyCode(tab.code)" title="复制">
            <span v-if="copied === tab.id">✓</span>
            <span v-else>📋</span>
          </button>
        </div>
        <pre :class="`language-${tab.language || 'text'}`"><code v-html="highlightedCode(tab)"></code></pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Tab {
  id: string
  label: string
  code: string
  language?: string
  filename?: string
  icon?: string
}

interface Props {
  tabs: Tab[]
  defaultTab?: string
}

const props = withDefaults(defineProps<Props>(), {
  defaultTab: undefined
})

const activeTab = ref(props.defaultTab || props.tabs[0]?.id)
const copied = ref<string | null>(null)

// Simple syntax highlighting
const highlightedCode = (tab: Tab): string => {
  let code = escapeHtml(tab.code)
  const lang = tab.language || 'text'
  
  if (lang === 'json') {
    // JSON highlighting
    code = code
      .replace(/(".*?"):/g, '<span class="token-key">$1</span>:')
      .replace(/: (".*?")/g, ': <span class="token-string">$1</span>')
      .replace(/: (\d+)/g, ': <span class="token-number">$1</span>')
      .replace(/: (true|false|null)/g, ': <span class="token-boolean">$1</span>')
  } else if (lang === 'bash' || lang === 'shell' || lang === 'sh') {
    // Shell highlighting
    code = code
      .replace(/(#.*$)/gm, '<span class="token-comment">$1</span>')
      .replace(/\b(cleanbook|pip|python|npm|yarn)\b/g, '<span class="token-command">$1</span>')
      .replace(/(-[-\w]+)/g, '<span class="token-flag">$1</span>')
  } else if (lang === 'python' || lang === 'py') {
    // Python highlighting
    code = code
      .replace(/(#.*$)/gm, '<span class="token-comment">$1</span>')
      .replace(/\b(def|class|import|from|return|if|else|elif|for|while|try|except|with|as)\b/g, '<span class="token-keyword">$1</span>')
      .replace(/("""[\s\S]*?""")/g, '<span class="token-string">$1</span>')
      .replace(/('.*?')/g, '<span class="token-string">$1</span>')
      .replace(/(".*?")/g, '<span class="token-string">$1</span>')
  } else if (lang === 'yaml' || lang === 'yml') {
    // YAML highlighting
    code = code
      .replace(/(#.*$)/gm, '<span class="token-comment">$1</span>')
      .replace(/^(\w+):/gm, '<span class="token-key">$1</span>:')
  }
  
  return code
}

const escapeHtml = (unsafe: string): string => {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

const copyCode = async (code: string) => {
  try {
    await navigator.clipboard.writeText(code)
    copied.value = activeTab.value
    setTimeout(() => {
      copied.value = null
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.code-group {
  border-radius: var(--cb-radius-lg);
  overflow: hidden;
  box-shadow: var(--cb-shadow-md);
  margin: 1.5rem 0;
  background: #0f172a;
}

.code-group-tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  padding: 0 0.5rem;
  gap: 0.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.code-group-tab {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.75rem 1rem;
  font-size: 0.8125rem;
  color: var(--cb-gray-400);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--cb-font-sans);
  font-weight: 500;
}

.code-group-tab:hover {
  color: var(--cb-gray-200);
}

.code-group-tab.active {
  color: var(--cb-brand-light);
  border-bottom-color: var(--cb-brand);
}

.tab-icon {
  font-size: 0.875rem;
}

.code-group-content {
  position: relative;
}

.code-group-panel {
  display: none;
}

.code-group-panel.active {
  display: block;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.code-filename {
  font-size: 0.75rem;
  color: var(--cb-gray-500);
  font-family: var(--cb-font-mono);
}

.code-copy {
  background: transparent;
  border: none;
  color: var(--cb-gray-500);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.25rem;
  border-radius: var(--cb-radius-sm);
  transition: all 0.2s ease;
}

.code-copy:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--cb-gray-300);
}

pre {
  margin: 0;
  padding: 1.25rem;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.6;
  font-family: var(--cb-font-mono);
}

code {
  color: #e2e8f0;
}

/* Syntax Tokens */
:deep(.token-key) {
  color: #7dd3fc;
}

:deep(.token-string) {
  color: #86efac;
}

:deep(.token-number) {
  color: #fca5a5;
}

:deep(.token-boolean) {
  color: #c4b5fd;
}

:deep(.token-comment) {
  color: var(--cb-gray-500);
  font-style: italic;
}

:deep(.token-command) {
  color: #fde047;
  font-weight: 600;
}

:deep(.token-flag) {
  color: #fdba74;
}

:deep(.token-keyword) {
  color: #c4b5fd;
  font-weight: 600;
}

pre::-webkit-scrollbar {
  height: 8px;
}

pre::-webkit-scrollbar-track {
  background: transparent;
}

pre::-webkit-scrollbar-thumb {
  background: var(--cb-gray-700);
  border-radius: 4px;
}

pre::-webkit-scrollbar-thumb:hover {
  background: var(--cb-gray-600);
}
</style>
