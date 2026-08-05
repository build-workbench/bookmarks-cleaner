import test from 'node:test'
import assert from 'node:assert/strict'

import { getLandingContent } from '../.vitepress/theme/home-content.mjs'

test('landing content exposes architecture-first entry points and evidence in Chinese', () => {
  const content = getLandingContent()

  assert.equal(content.metrics.length, 4)
  assert.equal(content.paths.length, 5)
  assert.equal(content.evidence.length, 4)
  assert.ok(content.metrics.some((item) => item.label === '处理速度'))
  assert.ok(content.paths.some((item) => item.href === '/zh/whitepaper'))
  assert.ok(content.evidence.some((item) => item.title.includes('融合')))
})
