import test from 'node:test'
import assert from 'node:assert/strict'

import { createThemeConfig } from '../.vitepress/shared/site-data.mjs'

function collectLinks(items) {
  return items.flatMap((item) => {
    const links = item.link ? [item.link] : []
    const nested = item.items ? collectLinks(item.items) : []
    return [...links, ...nested]
  })
}

test('theme config keeps the research reading order in Chinese', () => {
  const config = createThemeConfig()

  assert.deepEqual(
    config.nav.map((item) => item.text),
    ['导读', '架构', '算法', '性能', '白皮书', '参考', 'GitHub'],
  )

  const referenceLinks = collectLinks(config.sidebar['/zh/reference/'][0].items)
  assert.ok(!referenceLinks.includes('/zh/reference/api'))
})
