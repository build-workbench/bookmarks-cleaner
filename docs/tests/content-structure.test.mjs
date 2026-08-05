import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'

const docsRoot = join(process.cwd())

function read(relativePath) {
  return readFileSync(join(docsRoot, relativePath), 'utf8')
}

test('chinese whitepaper and pipeline pages expose the research-grade structure', () => {
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
