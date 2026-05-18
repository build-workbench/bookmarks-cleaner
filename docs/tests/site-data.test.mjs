import test from 'node:test'
import assert from 'node:assert/strict'

import {
  createLocaleThemeConfig,
  resolvePreferredLocale,
} from '../.vitepress/shared/site-data.mjs'

function collectLinks(items) {
  return items.flatMap((item) => {
    const links = item.link ? [item.link] : []
    const nested = item.items ? collectLinks(item.items) : []
    return [...links, ...nested]
  })
}

test('resolvePreferredLocale keeps an explicit stored locale', () => {
  assert.equal(resolvePreferredLocale('en', 'zh-CN'), 'en')
  assert.equal(resolvePreferredLocale('zh', 'en-US'), 'zh')
})

test('resolvePreferredLocale falls back to browser language only when no stored locale exists', () => {
  assert.equal(resolvePreferredLocale(null, 'zh-CN'), 'zh')
  assert.equal(resolvePreferredLocale(undefined, 'en-US'), 'en')
})

test('locale theme config keeps the research reading order and omits the missing Python API page', () => {
  const enConfig = createLocaleThemeConfig('en')
  const zhConfig = createLocaleThemeConfig('zh')

  assert.deepEqual(
    enConfig.nav.map((item) => item.text),
    ['Overview', 'Architecture', 'Algorithms', 'Performance', 'Whitepaper', 'References', 'GitHub'],
  )
  assert.deepEqual(
    zhConfig.nav.map((item) => item.text),
    ['导读', '架构', '算法', '性能', '白皮书', '参考', 'GitHub'],
  )

  const enReferenceLinks = collectLinks(enConfig.sidebar['/en/reference/'][0].items)
  const zhReferenceLinks = collectLinks(zhConfig.sidebar['/zh/reference/'][0].items)

  assert.ok(!enReferenceLinks.includes('/en/reference/api'))
  assert.ok(!zhReferenceLinks.includes('/zh/reference/api'))
})
