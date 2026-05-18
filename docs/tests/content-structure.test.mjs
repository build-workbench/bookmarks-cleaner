import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'

const docsRoot = join(process.cwd())

function read(relativePath) {
  return readFileSync(join(docsRoot, relativePath), 'utf8')
}

test('english whitepaper and pipeline pages expose the new research-grade structure', () => {
  const whitepaper = read('en/whitepaper.md')
  const pipeline = read('en/architecture/pipeline.md')
  const related = read('en/resources/related-projects.md')

  assert.match(whitepaper, /^## System Thesis$/m)
  assert.match(whitepaper, /^## Runtime Boundary$/m)
  assert.match(whitepaper, /^## Performance Methodology$/m)
  assert.match(whitepaper, /^## Failure Modes and Fallbacks$/m)

  assert.match(pipeline, /^## Runtime Layers$/m)
  assert.match(pipeline, /^### Entry and orchestration$/m)
  assert.match(related, /^## Comparative Frame$/m)
})

test('chinese whitepaper and pipeline pages mirror the same technical structure', () => {
  const whitepaper = read('zh/whitepaper.md')
  const pipeline = read('zh/architecture/pipeline.md')
  const related = read('zh/resources/related-projects.md')

  assert.match(whitepaper, /^## 系统命题$/m)
  assert.match(whitepaper, /^## 运行时边界$/m)
  assert.match(whitepaper, /^## 性能方法学$/m)
  assert.match(whitepaper, /^## 失败模式与回退策略$/m)

  assert.match(pipeline, /^## 运行时分层$/m)
  assert.match(pipeline, /^### 入口与协调$/m)
  assert.match(related, /^## 对比框架$/m)
})
