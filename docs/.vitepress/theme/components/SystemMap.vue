<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'

const { lang } = useData()
const isZh = computed(() => lang.value === 'zh-CN')

const labels = computed(() => isZh.value ? {
  title: '系统总览',
  subtitle: '入口、协调、流水线、分类智能体与导出层之间的运行时关系。',
  entry: '入口层',
  facade: '门面层',
  orchestration: '协调层',
  pipeline: '处理流水线',
  intelligence: '分类智能层',
  outputs: '输出层',
  notes: ['CLI / Python API', 'BookmarkProcessor / Container', 'Loader → Dedup → Classify → Organize → Export', 'Rules / ML / Semantic / LLM / Fusion'],
} : {
  title: 'System map',
  subtitle: 'Runtime relationship between entry surfaces, orchestration, processing stages, intelligence modules, and outputs.',
  entry: 'Entry',
  facade: 'Facade',
  orchestration: 'Orchestration',
  pipeline: 'Pipeline',
  intelligence: 'Intelligence',
  outputs: 'Outputs',
  notes: ['CLI / Python API', 'BookmarkProcessor / Container', 'Loader → Dedup → Classify → Organize → Export', 'Rules / ML / Semantic / LLM / Fusion'],
})
</script>

<template>
  <section class="cb-system-map-shell">
    <header class="cb-system-map-header">
      <h2>{{ labels.title }}</h2>
      <p>{{ labels.subtitle }}</p>
    </header>

    <div class="cb-system-map-frame">
      <svg viewBox="0 0 1080 620" class="cb-system-map" role="img" aria-label="System map">
        <g class="cb-layer">
          <rect x="32" y="32" width="188" height="104" rx="24" class="cb-box cb-box-entry" />
          <text x="56" y="74" class="cb-label">{{ labels.entry }}</text>
          <text x="56" y="110" class="cb-sub">CLI / Python API</text>
        </g>

        <g class="cb-layer">
          <rect x="270" y="32" width="220" height="104" rx="24" class="cb-box cb-box-core" />
          <text x="296" y="74" class="cb-label">{{ labels.facade }}</text>
          <text x="296" y="110" class="cb-sub">BookmarkProcessor</text>
        </g>

        <g class="cb-layer">
          <rect x="540" y="32" width="224" height="104" rx="24" class="cb-box cb-box-core" />
          <text x="566" y="74" class="cb-label">{{ labels.orchestration }}</text>
          <text x="566" y="110" class="cb-sub">Container → Coordinator</text>
        </g>

        <g class="cb-layer">
          <rect x="92" y="214" width="628" height="176" rx="30" class="cb-band" />
          <text x="122" y="258" class="cb-section">{{ labels.pipeline }}</text>

          <rect x="120" y="286" width="96" height="58" rx="18" class="cb-stage" />
          <rect x="242" y="286" width="96" height="58" rx="18" class="cb-stage" />
          <rect x="364" y="286" width="96" height="58" rx="18" class="cb-stage cb-stage-highlight" />
          <rect x="486" y="286" width="96" height="58" rx="18" class="cb-stage" />
          <rect x="608" y="286" width="96" height="58" rx="18" class="cb-stage" />

          <text x="148" y="321" class="cb-stage-text">Load</text>
          <text x="265" y="321" class="cb-stage-text">Dedup</text>
          <text x="388" y="321" class="cb-stage-text">Classify</text>
          <text x="507" y="321" class="cb-stage-text">Organize</text>
          <text x="634" y="321" class="cb-stage-text">Export</text>
        </g>

        <g class="cb-layer">
          <rect x="760" y="214" width="288" height="290" rx="30" class="cb-band cb-band-side" />
          <text x="790" y="258" class="cb-section">{{ labels.intelligence }}</text>

          <rect x="790" y="288" width="226" height="42" rx="14" class="cb-chip" />
          <rect x="790" y="344" width="226" height="42" rx="14" class="cb-chip" />
          <rect x="790" y="400" width="226" height="42" rx="14" class="cb-chip" />
          <rect x="790" y="456" width="226" height="42" rx="14" class="cb-chip cb-stage-highlight" />

          <text x="818" y="315" class="cb-chip-text">Rule Engine</text>
          <text x="818" y="371" class="cb-chip-text">ML / Semantic</text>
          <text x="818" y="427" class="cb-chip-text">Optional LLM</text>
          <text x="818" y="483" class="cb-chip-text">Fusion Engine</text>
        </g>

        <g class="cb-layer">
          <rect x="294" y="470" width="308" height="92" rx="24" class="cb-box cb-box-output" />
          <text x="320" y="510" class="cb-label">{{ labels.outputs }}</text>
          <text x="320" y="544" class="cb-sub">HTML report · JSON data · Markdown</text>
        </g>

        <g class="cb-wire">
          <path d="M220 84H270" />
          <path d="M490 84H540" />
          <path d="M652 136V214" />
          <path d="M412 136V214" />
          <path d="M460 315H790" />
          <path d="M448 390V470" />
        </g>
      </svg>
    </div>

    <ul class="cb-system-notes">
      <li v-for="note in labels.notes" :key="note">{{ note }}</li>
    </ul>
  </section>
</template>

<style scoped>
.cb-system-map-shell {
  margin: 2.5rem 0;
}

.cb-system-map-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.cb-system-map-header h2,
.cb-system-map-header p {
  margin: 0;
}

.cb-system-map-header h2 {
  color: var(--cb-text);
  font-size: 1.55rem;
}

.cb-system-map-header p {
  max-width: 48ch;
  color: var(--cb-text-3);
}

.cb-system-map-frame {
  border: 1px solid var(--cb-border);
  border-radius: 28px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--cb-accent) 4%, transparent), transparent 18%),
    var(--cb-bg-elevated);
  overflow: hidden;
  box-shadow: var(--cb-shadow-md);
}

.cb-system-map {
  display: block;
  width: 100%;
  height: auto;
}

.cb-box,
.cb-stage,
.cb-chip,
.cb-band {
  fill: var(--cb-bg);
  stroke: var(--cb-border-strong);
  stroke-width: 1.5;
}

.cb-box-entry {
  fill: color-mix(in srgb, var(--cb-accent) 7%, var(--cb-bg));
}

.cb-box-core {
  fill: color-mix(in srgb, var(--cb-support) 7%, var(--cb-bg));
}

.cb-box-output {
  fill: color-mix(in srgb, var(--cb-highlight) 10%, var(--cb-bg));
}

.cb-band {
  fill: color-mix(in srgb, var(--cb-bg-soft) 72%, var(--cb-bg));
}

.cb-stage-highlight {
  fill: color-mix(in srgb, var(--cb-accent) 12%, var(--cb-bg));
}

.cb-label,
.cb-section,
.cb-stage-text,
.cb-chip-text {
  fill: var(--cb-text);
  font-family: var(--cb-font-mono);
  font-weight: 700;
}

.cb-label {
  font-size: 22px;
}

.cb-section {
  font-size: 16px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.cb-sub {
  fill: var(--cb-text-3);
  font-size: 16px;
}

.cb-stage-text,
.cb-chip-text {
  font-size: 14px;
}

.cb-wire path {
  fill: none;
  stroke: color-mix(in srgb, var(--cb-accent) 55%, var(--cb-border-strong));
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.cb-system-notes {
  list-style: none;
  padding: 0;
  margin: 1rem 0 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.cb-system-notes li {
  padding: 0.85rem 1rem;
  border-radius: 14px;
  border: 1px solid var(--cb-border);
  background: var(--cb-bg-elevated);
  color: var(--cb-text-2);
}

@media (max-width: 760px) {
  .cb-system-notes {
    grid-template-columns: 1fr;
  }
}
</style>
