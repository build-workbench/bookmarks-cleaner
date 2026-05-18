<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'

const { lang } = useData()
const isZh = computed(() => lang.value === 'zh-CN')

type CellValue = 'yes' | 'no' | 'partial' | 'opt'

interface Row {
  feature: string
  cleanbook: CellValue
  linkding: CellValue
  shaarli: CellValue
}

const content = computed(() => isZh.value ? {
  title: '架构对比矩阵',
  subtitle: 'CleanBook 与主流同类工具在核心设计维度上的对比。',
  tools: ['CleanBook', 'linkding', 'Shaarli'],
  rows: [
    { feature: '离线优先（无服务端依赖）', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
    { feature: '规则驱动分类', cleanbook: 'yes', linkding: 'no', shaarli: 'partial' },
    { feature: 'ML 辅助分类', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
    { feature: 'LLM 可选集成', cleanbook: 'opt', linkding: 'no', shaarli: 'no' },
    { feature: '融合多分类器', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
    { feature: '导出到 HTML/JSON/MD', cleanbook: 'yes', linkding: 'partial', shaarli: 'partial' },
    { feature: '无遥测 · 数据不离本机', cleanbook: 'yes', linkding: 'partial', shaarli: 'yes' },
    { feature: 'CLI 入口', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
    { feature: 'Python 可编程 API', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
  ] as Row[],
  legend: { yes: '完整支持', no: '不支持', partial: '部分支持', opt: '可选启用' },
} : {
  title: 'Architecture Comparison',
  subtitle: 'CleanBook vs mainstream tools on core design dimensions.',
  tools: ['CleanBook', 'linkding', 'Shaarli'],
  rows: [
    { feature: 'Offline-first (no server)', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
    { feature: 'Rules-driven classification', cleanbook: 'yes', linkding: 'no', shaarli: 'partial' },
    { feature: 'ML-assisted classification', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
    { feature: 'Optional LLM integration', cleanbook: 'opt', linkding: 'no', shaarli: 'no' },
    { feature: 'Multi-classifier fusion', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
    { feature: 'Export HTML / JSON / MD', cleanbook: 'yes', linkding: 'partial', shaarli: 'partial' },
    { feature: 'No telemetry · local-only', cleanbook: 'yes', linkding: 'partial', shaarli: 'yes' },
    { feature: 'CLI entry point', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
    { feature: 'Programmable Python API', cleanbook: 'yes', linkding: 'no', shaarli: 'no' },
  ] as Row[],
  legend: { yes: 'Full support', no: 'Not supported', partial: 'Partial', opt: 'Optional' },
})

function cellClass(v: CellValue) {
  return {
    'cb-cell-yes': v === 'yes',
    'cb-cell-no': v === 'no',
    'cb-cell-partial': v === 'partial',
    'cb-cell-opt': v === 'opt',
  }
}

const SYMBOLS: Record<CellValue, string> = {
  yes: '✓',
  no: '✗',
  partial: '◑',
  opt: '⊙',
}
</script>

<template>
  <section class="cb-arch-matrix">
    <header class="cb-arch-header">
      <h3>{{ content.title }}</h3>
      <p>{{ content.subtitle }}</p>
    </header>

    <div class="cb-arch-table-wrap">
      <table class="cb-arch-table">
        <thead>
          <tr>
            <th class="cb-col-feature">{{ isZh ? '功能维度' : 'Dimension' }}</th>
            <th
              v-for="(tool, idx) in content.tools"
              :key="tool"
              :class="['cb-col-tool', { 'cb-col-highlight': idx === 0 }]"
            >
              {{ tool }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in content.rows" :key="row.feature">
            <td class="cb-cell-feature">{{ row.feature }}</td>
            <td
              v-for="(tool, idx) in content.tools"
              :key="tool"
              :class="['cb-cell-val', cellClass(row[tool.toLowerCase().replace('cleanbook', 'cleanbook') as 'cleanbook' | 'linkding' | 'shaarli']), { 'cb-col-highlight': idx === 0 }]"
            >
              <span class="cb-cell-symbol">{{ SYMBOLS[row[['cleanbook', 'linkding', 'shaarli'][idx] as 'cleanbook' | 'linkding' | 'shaarli']] }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ul class="cb-arch-legend">
      <li v-for="(label, key) in content.legend" :key="key" :class="`cb-legend-${key}`">
        <span class="cb-legend-sym">{{ SYMBOLS[key as CellValue] }}</span>
        {{ label }}
      </li>
    </ul>
  </section>
</template>

<style scoped>
.cb-arch-matrix {
  margin: 2.25rem 0;
}

.cb-arch-header {
  margin-bottom: 1.1rem;
}

.cb-arch-header h3,
.cb-arch-header p {
  margin: 0;
}

.cb-arch-header h3 {
  color: var(--cb-text);
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.025em;
}

.cb-arch-header p {
  margin-top: 0.3rem;
  color: var(--cb-text-3);
  font-size: 0.88rem;
}

.cb-arch-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--cb-border);
  border-radius: var(--cb-radius-lg);
  box-shadow: var(--cb-shadow-sm);
}

.cb-arch-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--cb-bg-elevated);
  font-size: 0.91rem;
  margin: 0 !important;
  border: none !important;
  border-radius: 0 !important;
}

.cb-arch-table thead tr {
  background: color-mix(in srgb, var(--cb-bg-soft) 70%, var(--cb-bg-elevated));
}

.cb-arch-table th {
  padding: 0.9rem 1rem;
  font-weight: 800;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-family: var(--cb-font-mono);
  color: var(--cb-text);
  border-bottom: 1px solid var(--cb-border);
  text-align: center;
}

.cb-arch-table th.cb-col-feature {
  text-align: left;
  min-width: 220px;
}

.cb-arch-table th.cb-col-highlight {
  color: var(--cb-accent);
  background: color-mix(in srgb, var(--cb-accent) 6%, transparent);
}

.cb-arch-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--cb-border);
  text-align: center;
  vertical-align: middle;
}

.cb-arch-table tr:last-child td {
  border-bottom: none;
}

.cb-arch-table tr:nth-child(2n) {
  background: color-mix(in srgb, var(--cb-bg-soft) 40%, transparent);
}

.cb-cell-feature {
  text-align: left !important;
  color: var(--cb-text-2);
  font-size: 0.91rem;
}

.cb-col-highlight {
  background: color-mix(in srgb, var(--cb-accent) 4%, transparent) !important;
}

.cb-cell-symbol {
  font-size: 1.1rem;
  font-weight: 700;
  font-family: var(--cb-font-mono);
}

.cb-cell-yes .cb-cell-symbol { color: var(--cb-support); }
.cb-cell-no .cb-cell-symbol { color: var(--cb-text-muted); }
.cb-cell-partial .cb-cell-symbol { color: var(--cb-highlight); }
.cb-cell-opt .cb-cell-symbol { color: var(--cb-accent); }

/* Legend */
.cb-arch-legend {
  list-style: none;
  padding: 0;
  margin: 0.85rem 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.25rem;
}

.cb-arch-legend li {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--cb-text-3);
  font-family: var(--cb-font-mono);
}

.cb-legend-sym {
  font-size: 0.95rem;
  font-weight: 700;
}

.cb-legend-yes .cb-legend-sym { color: var(--cb-support); }
.cb-legend-no .cb-legend-sym { color: var(--cb-text-muted); }
.cb-legend-partial .cb-legend-sym { color: var(--cb-highlight); }
.cb-legend-opt .cb-legend-sym { color: var(--cb-accent); }
</style>
