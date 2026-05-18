import test from 'node:test'
import assert from 'node:assert/strict'

import { getLandingContent } from '../.vitepress/theme/home-content.mjs'

test('english landing content exposes architecture-first entry points and evidence', () => {
  const en = getLandingContent('en')

  assert.equal(en.metrics.length, 4)
  assert.equal(en.paths.length, 4)
  assert.equal(en.evidence.length, 4)
  assert.ok(en.metrics.some((item) => item.label === 'Throughput'))
  assert.ok(en.paths.some((item) => item.href === '/en/whitepaper'))
  assert.ok(en.evidence.some((item) => item.title.includes('Fusion')))
})

test('chinese landing content mirrors the same structure', () => {
  const zh = getLandingContent('zh')

  assert.equal(zh.metrics.length, 4)
  assert.equal(zh.paths.length, 4)
  assert.equal(zh.evidence.length, 4)
  assert.ok(zh.metrics.some((item) => item.label === '处理速度'))
  assert.ok(zh.paths.some((item) => item.href === '/zh/whitepaper'))
  assert.ok(zh.evidence.some((item) => item.title.includes('融合')))
})
