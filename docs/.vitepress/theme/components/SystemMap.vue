<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'

const { lang, isDark } = useData()
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
  notes: [
    'CLI / Python API — 入口层保持收敛',
    'BookmarkProcessor 作为系统门面',
    'Loader → Dedup → Classify → Organize → Export',
    'Rules / ML / Semantic / LLM / Fusion'
  ],
} : {
  title: 'System Map',
  subtitle: 'Runtime relationship between entry surfaces, orchestration, pipeline stages, intelligence, and outputs.',
  entry: 'Entry',
  facade: 'Facade',
  orchestration: 'Orchestration',
  pipeline: 'Processing Pipeline',
  intelligence: 'Intelligence Layer',
  outputs: 'Outputs',
  notes: [
    'CLI / Python API — entry surface stays convergent',
    'BookmarkProcessor acts as system facade',
    'Loader → Dedup → Classify → Organize → Export',
    'Rules / ML / Semantic / LLM / Fusion'
  ],
})

// Use explicit hex values for both modes — no CSS variable injection into SVG
const colors = computed(() => isDark.value ? {
  bg: '#1a1e28',
  bgElevated: '#222736',
  bgBand: '#1e2234',
  bgBandSide: '#1c2030',
  text: '#eef0f5',
  textSub: '#8b93a8',
  textSection: '#a0a8be',
  border: '#343d54',
  borderStrong: '#4a556e',
  accent: '#7eb3ff',
  accentFill: 'rgba(126,179,255,0.12)',
  support: '#5ecfca',
  supportFill: 'rgba(94,207,202,0.10)',
  highlight: '#f0c060',
  highlightFill: 'rgba(240,192,96,0.14)',
  wire: '#5a8ccc',
  stageHighlight: 'rgba(126,179,255,0.16)',
} : {
  bg: '#ffffff',
  bgElevated: '#fafbfd',
  bgBand: '#f4f6fb',
  bgBandSide: '#f0f3f9',
  text: '#1a1e2e',
  textSub: '#5a6480',
  textSection: '#6b7494',
  border: '#d8dce8',
  borderStrong: '#c2c8da',
  accent: '#2055cc',
  accentFill: 'rgba(32,85,204,0.07)',
  support: '#0e8c84',
  supportFill: 'rgba(14,140,132,0.07)',
  highlight: '#b87000',
  highlightFill: 'rgba(184,112,0,0.08)',
  wire: '#4477cc',
  stageHighlight: 'rgba(32,85,204,0.09)',
})
</script>

<template>
  <section class="cb-system-map-shell">
    <header class="cb-system-map-header">
      <h2>{{ labels.title }}</h2>
      <p>{{ labels.subtitle }}</p>
    </header>

    <div class="cb-system-map-frame">
      <svg
        viewBox="0 0 1100 640"
        class="cb-system-map"
        role="img"
        :aria-label="labels.title"
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- Background -->
        <rect width="1100" height="640" :fill="colors.bg" />

        <!-- ── Entry Layer ── -->
        <rect x="28" y="28" width="196" height="108" rx="20"
          :fill="colors.accentFill" :stroke="colors.accent" stroke-width="1.5"/>
        <text x="48" y="65" font-family="JetBrains Mono, monospace" font-weight="700" font-size="18"
          :fill="colors.text">{{ labels.entry }}</text>
        <text x="48" y="100" font-family="JetBrains Mono, monospace" font-size="13"
          :fill="colors.textSub">CLI / Python API</text>

        <!-- ── Facade Layer ── -->
        <rect x="268" y="28" width="224" height="108" rx="20"
          :fill="colors.supportFill" :stroke="colors.support" stroke-width="1.5"/>
        <text x="288" y="65" font-family="JetBrains Mono, monospace" font-weight="700" font-size="18"
          :fill="colors.text">{{ labels.facade }}</text>
        <text x="288" y="100" font-family="JetBrains Mono, monospace" font-size="13"
          :fill="colors.textSub">BookmarkProcessor</text>

        <!-- ── Orchestration Layer ── -->
        <rect x="540" y="28" width="236" height="108" rx="20"
          :fill="colors.supportFill" :stroke="colors.support" stroke-width="1.5"/>
        <text x="560" y="65" font-family="JetBrains Mono, monospace" font-weight="700" font-size="18"
          :fill="colors.text">{{ labels.orchestration }}</text>
        <text x="560" y="100" font-family="JetBrains Mono, monospace" font-size="13"
          :fill="colors.textSub">Container → Coordinator</text>

        <!-- ── Pipeline Band ── -->
        <rect x="60" y="210" width="690" height="188" rx="26"
          :fill="colors.bgBand" :stroke="colors.border" stroke-width="1.5"/>
        <text x="84" y="252" font-family="JetBrains Mono, monospace" font-weight="700" font-size="12"
          text-transform="uppercase" letter-spacing="0.1em" :fill="colors.textSection">
          {{ labels.pipeline }}
        </text>

        <!-- Stage: Load -->
        <rect x="82" y="272" width="106" height="96" rx="16"
          :fill="colors.bgElevated" :stroke="colors.borderStrong" stroke-width="1.5"/>
        <text x="135" y="316" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.text">Load</text>
        <text x="135" y="337" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-size="11" :fill="colors.textSub">HTML/JSON</text>

        <!-- Stage: Deduplicate -->
        <rect x="218" y="272" width="106" height="96" rx="16"
          :fill="colors.bgElevated" :stroke="colors.borderStrong" stroke-width="1.5"/>
        <text x="271" y="316" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.text">Dedup</text>
        <text x="271" y="337" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-size="11" :fill="colors.textSub">Hash + Sim</text>

        <!-- Stage: Classify (highlighted) -->
        <rect x="354" y="272" width="106" height="96" rx="16"
          :fill="colors.stageHighlight" :stroke="colors.accent" stroke-width="2"/>
        <text x="407" y="316" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.accent">Classify</text>
        <text x="407" y="337" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-size="11" :fill="colors.textSub">Rules + ML</text>

        <!-- Stage: Organize -->
        <rect x="490" y="272" width="106" height="96" rx="16"
          :fill="colors.bgElevated" :stroke="colors.borderStrong" stroke-width="1.5"/>
        <text x="543" y="316" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.text">Organize</text>
        <text x="543" y="337" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-size="11" :fill="colors.textSub">Build Tree</text>

        <!-- Stage: Export -->
        <rect x="626" y="272" width="106" height="96" rx="16"
          :fill="colors.bgElevated" :stroke="colors.borderStrong" stroke-width="1.5"/>
        <text x="679" y="316" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.text">Export</text>
        <text x="679" y="337" text-anchor="middle" font-family="JetBrains Mono, monospace"
          font-size="11" :fill="colors.textSub">HTML/JSON/MD</text>

        <!-- Pipeline connectors (mini arrows between stages) -->
        <path d="M188 320 H218" :stroke="colors.wire" stroke-width="2" stroke-dasharray="4 3" fill="none"/>
        <path d="M324 320 H354" :stroke="colors.wire" stroke-width="2" stroke-dasharray="4 3" fill="none"/>
        <path d="M460 320 H490" :stroke="colors.wire" stroke-width="2" stroke-dasharray="4 3" fill="none"/>
        <path d="M596 320 H626" :stroke="colors.wire" stroke-width="2" stroke-dasharray="4 3" fill="none"/>

        <!-- ── Intelligence Band (right) ── -->
        <rect x="800" y="130" width="272" height="334" rx="26"
          :fill="colors.bgBandSide" :stroke="colors.border" stroke-width="1.5"/>
        <text x="824" y="172" font-family="JetBrains Mono, monospace" font-weight="700" font-size="12"
          letter-spacing="0.1em" :fill="colors.textSection">
          {{ labels.intelligence }}
        </text>

        <!-- Intelligence chips -->
        <rect x="820" y="188" width="232" height="46" rx="12"
          :fill="colors.bgElevated" :stroke="colors.borderStrong" stroke-width="1.5"/>
        <text x="844" y="217" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.text">Rule Engine</text>
        <text x="1032" y="217" text-anchor="end" font-family="JetBrains Mono, monospace"
          font-size="11" :fill="colors.accent">P=1.0</text>

        <rect x="820" y="248" width="232" height="46" rx="12"
          :fill="colors.bgElevated" :stroke="colors.borderStrong" stroke-width="1.5"/>
        <text x="844" y="277" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.text">ML Classifier</text>
        <text x="1032" y="277" text-anchor="end" font-family="JetBrains Mono, monospace"
          font-size="11" :fill="colors.textSub">TF-IDF</text>

        <rect x="820" y="308" width="232" height="46" rx="12"
          :fill="colors.bgElevated" :stroke="colors.borderStrong" stroke-width="1.5"/>
        <text x="844" y="337" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.text">Semantic</text>
        <text x="1032" y="337" text-anchor="end" font-family="JetBrains Mono, monospace"
          font-size="11" :fill="colors.textSub">Embed</text>

        <rect x="820" y="368" width="232" height="46" rx="12"
          :fill="colors.bgElevated" :stroke="colors.borderStrong" stroke-width="1.5"/>
        <text x="844" y="397" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.textSub">LLM (optional)</text>

        <rect x="820" y="418" width="232" height="46" rx="12"
          :fill="colors.stageHighlight" :stroke="colors.accent" stroke-width="2"/>
        <text x="844" y="447" font-family="JetBrains Mono, monospace"
          font-weight="700" font-size="14" :fill="colors.accent">Fusion Engine</text>
        <text x="1032" y="447" text-anchor="end" font-family="JetBrains Mono, monospace"
          font-size="11" :fill="colors.accent">∑w·c</text>

        <!-- ── Outputs Block ── -->
        <rect x="272" y="488" width="312" height="108" rx="20"
          :fill="colors.highlightFill" :stroke="colors.highlight" stroke-width="1.5"/>
        <text x="296" y="528" font-family="JetBrains Mono, monospace" font-weight="700" font-size="18"
          :fill="colors.text">{{ labels.outputs }}</text>
        <text x="296" y="560" font-family="JetBrains Mono, monospace" font-size="13"
          :fill="colors.textSub">HTML · JSON · Markdown</text>

        <!-- ── Wiring ── -->
        <!-- Entry → Facade -->
        <path d="M224 82 L268 82" :stroke="colors.wire" stroke-width="2.5" fill="none"
          stroke-linecap="round"/>
        <polygon :points="`262,77 268,82 262,87`" :fill="colors.wire"/>

        <!-- Facade → Orchestration -->
        <path d="M492 82 L540 82" :stroke="colors.wire" stroke-width="2.5" fill="none"
          stroke-linecap="round"/>
        <polygon :points="`534,77 540,82 534,87`" :fill="colors.wire"/>

        <!-- Orchestration → Pipeline band -->
        <path d="M658 136 L658 180 Q658 210 628 210" :stroke="colors.wire" stroke-width="2.5"
          fill="none" stroke-linecap="round" stroke-linejoin="round"/>

        <!-- Entry → Pipeline entry -->
        <path d="M126 136 L126 180 Q126 210 144 210" :stroke="colors.wire" stroke-width="2"
          fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 4"/>

        <!-- Pipeline → Intelligence (Classify stage) -->
        <path d="M460 320 L800 320" :stroke="colors.accent" stroke-width="2.5" fill="none"
          stroke-linecap="round" stroke-dasharray="8 4"/>

        <!-- Intelligence → Pipeline (fusion feedback) -->
        <path d="M800 441 L732 441 L732 370" :stroke="colors.accent" stroke-width="2"
          fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="5 3"
          opacity="0.6"/>

        <!-- Pipeline → Outputs -->
        <path d="M428 398 L428 488" :stroke="colors.wire" stroke-width="2.5"
          fill="none" stroke-linecap="round"/>
        <polygon :points="`423,482 428,488 433,482`" :fill="colors.wire"/>
      </svg>
    </div>

    <ul class="cb-system-notes">
      <li v-for="note in labels.notes" :key="note">{{ note }}</li>
    </ul>
  </section>
</template>

<style scoped>
.cb-system-map-shell {
  margin: 2.75rem 0;
}

.cb-system-map-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem 2rem;
  margin-bottom: 1.25rem;
}

.cb-system-map-header h2,
.cb-system-map-header p {
  margin: 0;
}

.cb-system-map-header h2 {
  color: var(--cb-text);
  font-size: 1.65rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.cb-system-map-header p {
  max-width: 52ch;
  color: var(--cb-text-3);
  font-size: 0.93rem;
  line-height: 1.7;
}

.cb-system-map-frame {
  border: 1px solid var(--cb-border);
  border-radius: var(--cb-radius-xl);
  background: var(--cb-bg-elevated);
  overflow: hidden;
  box-shadow: var(--cb-shadow-md);
  transition: border-color var(--cb-motion-normal);
}

.cb-system-map-frame:hover {
  border-color: var(--cb-border-accent);
}

.cb-system-map {
  display: block;
  width: 100%;
  height: auto;
}

.cb-system-notes {
  list-style: none;
  padding: 0;
  margin: 1.25rem 0 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.cb-system-notes li {
  padding: 0.9rem 1.1rem;
  border-radius: var(--cb-radius-md);
  border: 1px solid var(--cb-border);
  background: var(--cb-bg-elevated);
  color: var(--cb-text-2);
  font-size: 0.9rem;
  font-family: var(--cb-font-mono);
  transition: border-color var(--cb-motion-fast), background var(--cb-motion-fast);
}

.cb-system-notes li:hover {
  border-color: var(--cb-border-accent);
  background: color-mix(in srgb, var(--cb-accent) 4%, var(--cb-bg-elevated));
}

@media (max-width: 760px) {
  .cb-system-notes {
    grid-template-columns: 1fr;
  }

  .cb-system-map-header {
    flex-direction: column;
  }
}
</style>
