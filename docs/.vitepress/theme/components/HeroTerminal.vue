<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface OutputLine {
  id: number
  text: string
  type: 'success' | 'info' | 'normal'
}

const props = withDefaults(defineProps<{
  command?: string
  outputs?: string[]
  typingSpeed?: number
}>(), {
  command: 'cleanbook -i bookmarks.html -o output/',
  outputs: () => [
    '\u2713 加载书签文件: 1,247 个条目',
    '\u2713 去重完成: 移除 89 个重复项',
    '\u2713 分类完成: 12 个类别',
    '\u2713 导出完成: output/bookmarks_cleaned.html',
    '\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501',
    '\u5904\u7406\u7edf\u8ba1:',
    '  \u2022 总耗时: 2.3s',
    '  \u2022 处理速度: 542 书签/秒',
    '  \u2022 准确率: 96.8%',
  ],
  typingSpeed: 45
})

const displayedCommand = ref('')
const showCursor = ref(true)
const outputLines = ref<OutputLine[]>([])
const isTyping = ref(true)
const currentOutputIndex = ref(0)

let commandInterval: ReturnType<typeof setInterval> | null = null
let outputInterval: ReturnType<typeof setInterval> | null = null
let cursorInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  let charIndex = 0
  commandInterval = setInterval(() => {
    if (charIndex < props.command.length) {
      displayedCommand.value += props.command[charIndex]
      charIndex++
    } else {
      isTyping.value = false
      if (commandInterval) clearInterval(commandInterval)
      startOutput()
    }
  }, props.typingSpeed)

  cursorInterval = setInterval(() => {
    showCursor.value = !showCursor.value
  }, 530)
})

function startOutput() {
  outputInterval = setInterval(() => {
    if (currentOutputIndex.value < props.outputs.length) {
      const line = props.outputs[currentOutputIndex.value]
      let type: OutputLine['type'] = 'normal'
      if (line.startsWith('\u2713')) type = 'success'
      else if (line.startsWith('\u5904\u7406') || line.startsWith('\u2501')) type = 'info'

      outputLines.value.push({
        id: currentOutputIndex.value,
        text: line,
        type
      })
      currentOutputIndex.value++
    } else {
      if (outputInterval) clearInterval(outputInterval)
    }
  }, 180)
}

onUnmounted(() => {
  if (commandInterval) clearInterval(commandInterval)
  if (outputInterval) clearInterval(outputInterval)
  if (cursorInterval) clearInterval(cursorInterval)
})
</script>

<template>
  <div class="cb-terminal-container">
    <div class="cb-terminal">
      <div class="cb-terminal-header">
        <span class="cb-dot cb-dot-red"></span>
        <span class="cb-dot cb-dot-yellow"></span>
        <span class="cb-dot cb-dot-green"></span>
        <span class="cb-terminal-title">cleanbook</span>
        <span class="cb-terminal-badge">v1.0</span>
      </div>
      <div class="cb-terminal-body">
        <span class="cb-prompt">$</span>
        <span class="cb-command">{{ displayedCommand }}</span>
        <span v-if="isTyping" class="cb-cursor">\u258C</span>
      </div>
      <div v-if="outputLines.length > 0" class="cb-terminal-output">
        <p
          v-for="line in outputLines"
          :key="line.id"
          :class="['cb-line', `cb-line-${line.type}`]"
        >
          {{ line.text }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cb-terminal-container {
  margin: 32px 0;
}

.cb-terminal {
  background: var(--cb-bg-elevated);
  border-radius: 14px;
  border: 1px solid var(--cb-border);
  overflow: hidden;
  box-shadow: var(--cb-shadow-lg), var(--cb-glow);
  font-family: var(--cb-font-mono);
  transition: box-shadow var(--cb-motion-slow);
}

.cb-terminal:hover {
  box-shadow: var(--cb-shadow-lg), 0 0 60px rgba(0, 102, 255, 0.20);
}

.dark .cb-terminal:hover {
  box-shadow: var(--cb-shadow-lg), 0 0 60px rgba(77, 148, 255, 0.25);
}

.cb-terminal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--cb-bg-alt);
  border-bottom: 1px solid var(--cb-border);
}

.cb-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  box-shadow: inset 0 0 0 0.5px rgba(0,0,0,0.1);
}

.cb-dot-red { background: #FF5F56; }
.cb-dot-yellow { background: #FFBD2E; }
.cb-dot-green { background: #27CA40; }

.cb-terminal-title {
  margin-left: 8px;
  font-size: 12px;
  color: var(--cb-text-3);
  font-weight: 500;
}

.cb-terminal-badge {
  margin-left: auto;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--cb-brand-soft);
  color: var(--cb-brand);
  font-weight: 600;
}

.cb-terminal-body {
  padding: 20px;
  font-size: 15px;
  line-height: 1.6;
  min-height: 60px;
}

.cb-prompt {
  color: var(--cb-accent);
  margin-right: 10px;
  font-weight: 600;
}

.cb-command {
  color: var(--cb-text);
}

.cb-cursor {
  color: var(--cb-brand);
  animation: cb-blink 1s infinite;
  margin-left: 2px;
}

@keyframes cb-blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.cb-terminal-output {
  padding: 0 20px 20px;
  font-size: 13px;
  color: var(--cb-text-2);
  line-height: 1.7;
}

.cb-line {
  margin: 6px 0;
  white-space: pre;
  transition: color var(--cb-motion-fast);
}

.cb-line-success {
  color: var(--cb-accent);
  font-weight: 500;
}

.cb-line-info {
  color: var(--cb-brand);
  font-weight: 600;
}

@media (max-width: 640px) {
  .cb-terminal-body {
    padding: 16px;
    font-size: 13px;
  }

  .cb-terminal-output {
    padding: 0 16px 16px;
    font-size: 12px;
  }
}
</style>
