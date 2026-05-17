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
    '✓ 加载书签文件: 1,247 个条目',
    '✓ 去重完成: 移除 89 个重复项',
    '✓ 分类完成: 12 个类别',
    '✓ 导出完成: output/bookmarks_cleaned.html',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    '处理统计:',
    '  • 总耗时: 2.3s',
    '  • 处理速度: 542 书签/秒',
    '  • 准确率: 96.8%',
  ],
  typingSpeed: 50
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
  // Typing effect for command
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

  // Cursor blink
  cursorInterval = setInterval(() => {
    showCursor.value = !showCursor.value
  }, 530)
})

function startOutput() {
  outputInterval = setInterval(() => {
    if (currentOutputIndex.value < props.outputs.length) {
      const line = props.outputs[currentOutputIndex.value]
      let type: OutputLine['type'] = 'normal'
      if (line.startsWith('✓')) type = 'success'
      else if (line.startsWith('处理') || line.startsWith('━━')) type = 'info'

      outputLines.value.push({
        id: currentOutputIndex.value,
        text: line,
        type
      })
      currentOutputIndex.value++
    } else {
      if (outputInterval) clearInterval(outputInterval)
    }
  }, 200)
}

onUnmounted(() => {
  if (commandInterval) clearInterval(commandInterval)
  if (outputInterval) clearInterval(outputInterval)
  if (cursorInterval) clearInterval(cursorInterval)
})
</script>

<template>
  <div class="terminal-container">
    <div class="terminal">
      <div class="terminal-header">
        <span class="dot red"></span>
        <span class="dot yellow"></span>
        <span class="dot green"></span>
        <span class="title">Terminal — cleanbook</span>
      </div>
      <div class="terminal-body">
        <span class="prompt">$</span>
        <span class="command">{{ displayedCommand }}</span>
        <span v-if="isTyping" class="cursor">▌</span>
      </div>
      <div v-if="outputLines.length > 0" class="terminal-output">
        <p
          v-for="line in outputLines"
          :key="line.id"
          :class="['line', line.type]"
        >
          {{ line.text }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.terminal-container {
  margin: 32px 0;
}

.terminal {
  background: var(--vp-c-bg-elv);
  border-radius: 14px;
  border: 1px solid var(--vp-c-border);
  overflow: hidden;
  box-shadow: var(--cb-glow);
  font-family: var(--vp-font-family-mono);
}

.terminal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--vp-c-bg-alt);
  border-bottom: 1px solid var(--vp-c-border);
}

.terminal-header .dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.terminal-header .dot.red { background: #FF5F56; }
.terminal-header .dot.yellow { background: #FFBD2E; }
.terminal-header .dot.green { background: #27CA40; }

.terminal-header .title {
  margin-left: 12px;
  font-size: 13px;
  color: var(--vp-c-text-3);
}

.terminal-body {
  padding: 20px;
  font-size: 15px;
  line-height: 1.6;
  min-height: 60px;
}

.terminal-body .prompt {
  color: var(--vp-c-accent);
  margin-right: 10px;
  font-weight: 500;
}

.terminal-body .command {
  color: var(--vp-c-text-1);
}

.terminal-body .cursor {
  color: var(--vp-c-brand-1);
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.terminal-output {
  padding: 0 20px 20px;
  font-size: 13px;
  color: var(--vp-c-text-2);
  line-height: 1.7;
}

.terminal-output .line {
  margin: 6px 0;
  white-space: pre;
}

.terminal-output .line.success {
  color: var(--vp-c-accent);
}

.terminal-output .line.info {
  color: var(--vp-c-brand-1);
  font-weight: 500;
}

@media (max-width: 640px) {
  .terminal-body {
    padding: 16px;
    font-size: 13px;
  }

  .terminal-output {
    padding: 0 16px 16px;
    font-size: 12px;
  }
}
</style>
