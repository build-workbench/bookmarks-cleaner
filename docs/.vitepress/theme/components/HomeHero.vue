<template>
  <div class="home-hero" :class="{ 'is-loaded': isLoaded }">
    <div class="hero-particles">
      <div v-for="n in 6" :key="n" class="particle" :style="getParticleStyle(n)"></div>
    </div>
    
    <div class="hero-content">
      <div class="hero-badge" :class="{ 'animate-in': isLoaded }">
        <span class="badge-version">v{{ version }}</span>
        <span class="badge-separator">·</span>
        <span class="badge-status">{{ statusText }}</span>
      </div>
      
      <h1 class="hero-title" :class="{ 'animate-in': isLoaded }">
        <span class="title-gradient">CleanBook</span>
      </h1>
      
      <p class="hero-subtitle" :class="{ 'animate-in': isLoaded }">
        {{ subtitle }}
      </p>
      
      <p class="hero-description" :class="{ 'animate-in': isLoaded }">
        {{ description }}
      </p>
      
      <div class="hero-actions" :class="{ 'animate-in': isLoaded }">
        <a 
          v-for="(action, index) in actions" 
          :key="index"
          :href="action.link"
          class="hero-action"
          :class="action.theme || 'brand'"
        >
          {{ action.text }}
        </a>
      </div>
      
      <div class="hero-stats" :class="{ 'animate-in': isLoaded }" v-if="showStats">
        <div class="stat">
          <span class="stat-value">91.4%</span>
          <span class="stat-label">准确率</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-value">Offline</span>
          <span class="stat-label">优先</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-value">MIT</span>
          <span class="stat-label">开源</span>
        </div>
      </div>
    </div>
    
    <div class="hero-visual" :class="{ 'animate-in': isLoaded }">
      <div class="code-window">
        <div class="code-header">
          <span class="code-dot red"></span>
          <span class="code-dot yellow"></span>
          <span class="code-dot green"></span>
          <span class="code-filename">bookmarks.html</span>
        </div>
        <div class="code-body">
          <div class="code-line" v-for="(line, i) in codeLines" :key="i">
            <span class="line-number">{{ i + 1 }}</span>
            <span class="line-content" v-html="line"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Action {
  text: string
  link: string
  theme?: 'brand' | 'alt'
}

interface Props {
  version?: string
  statusText?: string
  subtitle?: string
  description?: string
  actions?: Action[]
  showStats?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  version: '2.0.0',
  statusText: '稳定版',
  subtitle: '智能书签清理与分类',
  description: '规则优先，ML 辅助，LLM 可选；默认离线可用的浏览器书签整理工具',
  actions: () => [
    { text: '快速开始 →', link: '/zh/quickstart', theme: 'brand' },
    { text: 'GitHub', link: 'https://github.com/LessUp/bookmarks-cleaner', theme: 'alt' }
  ],
  showStats: true
})

const isLoaded = ref(false)

const codeLines = [
  '<span class="token-tag">&lt;H3</span> <span class="token-attr">class</span>=<span class="token-string">"data"</span><span class="token-tag">&gt;</span>',
  '  <span class="token-tag">&lt;DT&gt;</span><span class="token-text">AI/ML</span><span class="token-tag">&lt;/DT&gt;</span>',
  '  <span class="token-tag">&lt;DL&gt;</span>',
  '    <span class="token-tag">&lt;p&gt;</span><span class="token-tag">&lt;A</span> <span class="token-attr">HREF</span>=<span class="token-string">"..."</span><span class="token-tag">&gt;</span>',
  '      <span class="token-text">🔥 PyTorch 文档</span>',
  '    <span class="token-tag">&lt;/A&gt;</span><span class="token-tag">&lt;/p&gt;</span>',
  '  <span class="token-tag">&lt;/DL&gt;</span>',
  '<span class="token-tag">&lt;/H3&gt;</span>'
]

const getParticleStyle = (n: number) => {
  const delays = [0, 2, 4, 1, 3, 5]
  const durations = [8, 10, 12, 9, 11, 13]
  const sizes = [4, 6, 3, 5, 4, 7]
  const lefts = [10, 25, 40, 60, 75, 90]
  
  return {
    animationDelay: `${delays[n - 1]}s`,
    animationDuration: `${durations[n - 1]}s`,
    width: `${sizes[n - 1]}px`,
    height: `${sizes[n - 1]}px`,
    left: `${lefts[n - 1]}%`
  }
}

onMounted(() => {
  setTimeout(() => {
    isLoaded.value = true
  }, 100)
})
</script>

<style scoped>
.home-hero {
  position: relative;
  padding: 6rem 0;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  min-height: 80vh;
}

/* Particles */
.hero-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.particle {
  position: absolute;
  top: 100%;
  border-radius: 50%;
  background: var(--cb-brand);
  opacity: 0.3;
  animation: float-up linear infinite;
}

@keyframes float-up {
  0% {
    top: 100%;
    opacity: 0;
    transform: translateX(0) rotate(0deg);
  }
  10% {
    opacity: 0.3;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    top: -10%;
    opacity: 0;
    transform: translateX(30px) rotate(360deg);
  }
}

/* Content */
.hero-content {
  position: relative;
  z-index: 1;
  max-width: 560px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.875rem;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--cb-radius-full);
  font-size: 0.8125rem;
  margin-bottom: 1.5rem;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease;
}

.hero-badge.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.badge-version {
  font-weight: 600;
  color: var(--cb-brand);
}

.badge-separator {
  color: var(--vp-c-text-3);
}

.badge-status {
  color: var(--vp-c-text-2);
}

.hero-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin: 0 0 1rem;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease 0.1s;
}

.hero-title.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.title-gradient {
  background: linear-gradient(135deg, var(--cb-brand) 0%, var(--cb-accent-purple) 50%, var(--cb-accent-cyan) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  background-size: 200% 200%;
  animation: gradient-shift 8s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.hero-subtitle {
  font-size: clamp(1.25rem, 2.5vw, 1.75rem);
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin: 0 0 0.75rem;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease 0.2s;
}

.hero-subtitle.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.hero-description {
  font-size: 1.125rem;
  color: var(--vp-c-text-2);
  line-height: 1.7;
  margin: 0 0 2rem;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease 0.3s;
}

.hero-description.animate-in {
  opacity: 1;
  transform: translateY(0);
}

/* Actions */
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2.5rem;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease 0.4s;
}

.hero-actions.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.hero-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.875rem 1.75rem;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  border-radius: var(--cb-radius);
  transition: all 0.3s ease;
}

.hero-action.brand {
  background: linear-gradient(135deg, var(--cb-brand) 0%, var(--cb-accent-purple) 100%);
  color: white;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.hero-action.brand:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}

.hero-action.alt {
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-divider);
}

.hero-action.alt:hover {
  border-color: var(--cb-brand);
  color: var(--cb-brand);
}

/* Stats */
.hero-stats {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease 0.5s;
}

.hero-stats.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--cb-brand), var(--cb-accent-purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--vp-c-divider);
}

/* Visual - Code Window */
.hero-visual {
  position: relative;
  opacity: 0;
  transform: translateX(40px);
  transition: all 0.8s ease 0.3s;
}

.hero-visual.animate-in {
  opacity: 1;
  transform: translateX(0);
}

.code-window {
  background: #0f172a;
  border-radius: var(--cb-radius-lg);
  overflow: hidden;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  transform: perspective(1000px) rotateY(-5deg) rotateX(2deg);
  transition: transform 0.5s ease;
}

.code-window:hover {
  transform: perspective(1000px) rotateY(0) rotateX(0);
}

.code-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.code-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.code-dot.red { background: #ff5f56; }
.code-dot.yellow { background: #ffbd2e; }
.code-dot.green { background: #27c93f; }

.code-filename {
  flex: 1;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--cb-gray-500);
  font-family: var(--cb-font-mono);
}

.code-body {
  padding: 1.25rem;
  font-family: var(--cb-font-mono);
  font-size: 0.8125rem;
  line-height: 1.8;
}

.code-line {
  display: flex;
  gap: 1rem;
}

.line-number {
  color: var(--cb-gray-600);
  text-align: right;
  min-width: 1.5rem;
  user-select: none;
}

.line-content {
  color: #e2e8f0;
}

:deep(.token-tag) { color: #f472b6; }
:deep(.token-attr) { color: #60a5fa; }
:deep(.token-string) { color: #86efac; }
:deep(.token-text) { color: #e2e8f0; }

/* Responsive */
@media (max-width: 900px) {
  .home-hero {
    grid-template-columns: 1fr;
    padding: 4rem 0;
    gap: 3rem;
  }
  
  .hero-visual {
    order: -1;
  }
  
  .code-window {
    transform: none;
    max-width: 500px;
    margin: 0 auto;
  }
}

@media (max-width: 480px) {
  .hero-actions {
    flex-direction: column;
  }
  
  .hero-action {
    width: 100%;
  }
  
  .hero-stats {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .stat-divider {
    display: none;
  }
}
</style>
