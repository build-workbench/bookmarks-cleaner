<template>
  <div class="terminal-demo" :class="{ 'is-playing': isPlaying }">
    <div class="terminal-header">
      <div class="terminal-dots">
        <span class="dot red"></span>
        <span class="dot yellow"></span>
        <span class="dot green"></span>
      </div>
      <span class="terminal-title">{{ title }}</span>
      <button 
        class="terminal-replay"
        @click="replay"
        :title="replayText"
      >
        ↻
      </button>
    </div>
    <div class="terminal-body" ref="terminalBody">
      <div 
        v-for="(line, index) in displayedLines" 
        :key="index"
        class="terminal-line"
        :class="{ 'is-output': line.type === 'output', 'is-error': line.type === 'error' }"
      >
        <template v-if="line.type === 'input'">
          <span class="terminal-prompt">{{ prompt }}</span>
          <span class="terminal-command">{{ line.content }}</span>
        </template>
        <template v-else>
          <pre class="terminal-output">{{ line.content }}</pre>
        </template>
      </div>
      <div v-if="isPlaying && currentLineIndex < lines.length" class="terminal-line">
        <span class="terminal-prompt">{{ prompt }}</span>
        <span class="terminal-typing">{{ typingText }}</span>
        <span class="terminal-cursor"></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'

interface Line {
  type: 'input' | 'output' | 'error'
  content: string
  delay?: number
}

interface Props {
  lines: Line[]
  title?: string
  prompt?: string
  replayText?: string
  typingSpeed?: number
  lineDelay?: number
  autoPlay?: boolean
  loop?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: 'cleanbook — zsh',
  prompt: '$',
  replayText: 'Replay',
  typingSpeed: 30,
  lineDelay: 500,
  autoPlay: true,
  loop: false
})

const terminalBody = ref<HTMLElement | null>(null)
const isPlaying = ref(false)
const currentLineIndex = ref(0)
const typingText = ref('')
const displayedLines = ref<Line[]>([])

const scrollToBottom = async () => {
  await nextTick()
  if (terminalBody.value) {
    terminalBody.value.scrollTop = terminalBody.value.scrollHeight
  }
}

const typeLine = async (line: Line): Promise<void> => {
  if (line.type !== 'input') {
    displayedLines.value.push(line)
    await scrollToBottom()
    return
  }

  isPlaying.value = true
  typingText.value = ''
  
  for (let i = 0; i < line.content.length; i++) {
    typingText.value += line.content[i]
    await new Promise(r => setTimeout(r, props.typingSpeed))
    await scrollToBottom()
  }
  
  displayedLines.value.push(line)
  typingText.value = ''
  isPlaying.value = false
  await scrollToBottom()
}

const play = async () => {
  currentLineIndex.value = 0
  displayedLines.value = []
  
  for (let i = 0; i < props.lines.length; i++) {
    currentLineIndex.value = i
    const line = props.lines[i]
    const delay = line.delay ?? props.lineDelay
    
    await new Promise(r => setTimeout(r, delay))
    await typeLine(line)
  }
  
  currentLineIndex.value = props.lines.length
  
  if (props.loop) {
    setTimeout(() => {
      play()
    }, 3000)
  }
}

const replay = () => {
  play()
}

watch(() => props.lines, () => {
  if (props.autoPlay) {
    play()
  }
}, { immediate: true })
</script>

<style scoped>
.terminal-demo {
  background: #0f172a;
  border-radius: var(--cb-radius-lg);
  overflow: hidden;
  box-shadow: 0 20px 50px -20px rgba(0, 0, 0, 0.5);
  font-family: var(--cb-font-mono);
  margin: 1.5rem 0;
}

.terminal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.terminal-dots {
  display: flex;
  gap: 0.5rem;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.red { background: #ff5f56; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #27c93f; }

.terminal-title {
  flex: 1;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--cb-gray-500);
  font-family: var(--cb-font-sans);
}

.terminal-replay {
  background: transparent;
  border: none;
  color: var(--cb-gray-500);
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
  transition: all 0.2s ease;
  border-radius: var(--cb-radius-sm);
}

.terminal-replay:hover {
  color: var(--cb-brand);
  background: rgba(255, 255, 255, 0.1);
}

.terminal-body {
  padding: 1rem 1.25rem;
  min-height: 180px;
  max-height: 400px;
  overflow-y: auto;
  font-size: 0.875rem;
  line-height: 1.6;
}

.terminal-line {
  margin-bottom: 0.5rem;
  min-height: 1.4em;
}

.terminal-prompt {
  color: var(--cb-accent-green);
  margin-right: 0.75rem;
  user-select: none;
}

.terminal-command {
  color: #e2e8f0;
}

.terminal-typing {
  color: #e2e8f0;
}

.terminal-output {
  color: var(--cb-gray-400);
  margin: 0.5rem 0 0.75rem 1.5rem;
  white-space: pre-wrap;
  word-break: break-word;
}

.terminal-line.is-error .terminal-output {
  color: var(--cb-accent-red);
}

.terminal-cursor {
  display: inline-block;
  width: 8px;
  height: 1.2em;
  background: var(--cb-brand);
  margin-left: 2px;
  animation: blink 1s step-end infinite;
  vertical-align: text-bottom;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* Scrollbar styling */
.terminal-body::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.terminal-body::-webkit-scrollbar-track {
  background: transparent;
}

.terminal-body::-webkit-scrollbar-thumb {
  background: var(--cb-gray-700);
  border-radius: 4px;
}

.terminal-body::-webkit-scrollbar-thumb:hover {
  background: var(--cb-gray-600);
}
</style>
