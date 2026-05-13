import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import llmstxt from 'vitepress-plugin-llms'

const rawBase = process.env.VITEPRESS_BASE
const base = rawBase
  ? rawBase.startsWith('/')
    ? rawBase.endsWith('/') ? rawBase : `${rawBase}/`
    : `/${rawBase}/`
  : '/'

const REPO = 'https://github.com/LessUp/bookmarks-cleaner'

function meta(lang: 'zh' | 'en'): any[] {
  const isZh = lang === 'zh'
  const description = isZh
    ? '开发者的离线优先书签清理与分类工具：规则优先，ML 辅助，LLM 可选。'
    : 'Offline-first bookmark cleaner for developers: rules-first, ML-assisted, LLM-optional.'
  const keywords = isZh
    ? '书签清理,书签分类,离线工具,Python CLI,规则引擎,机器学习'
    : 'bookmark cleaner,bookmark classification,offline tool,Python CLI,rules engine,machine learning'

  return [
    ['meta', { name: 'description', content: description }],
    ['meta', { name: 'keywords', content: keywords }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'Bookmarks Cleaner' }],
    ['meta', { property: 'og:description', content: description }],
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ['link', { rel: 'manifest', href: '/manifest.json' }],
  ]
}

export default withMermaid(defineConfig({
  base,
  title: 'Bookmarks Cleaner',
  description: 'Offline-first bookmark cleaner for developers',

  locales: {
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      link: '/zh/',
      title: 'Bookmarks Cleaner',
      description: '开发者的离线优先书签清理与分类工具：规则优先，ML 辅助，LLM 可选。',
      head: meta('zh'),
      themeConfig: {
        nav: [
          {
            text: '使用指南',
            items: [
              { text: '安装', link: '/zh/guide/installation' },
              { text: '配置', link: '/zh/guide/configuration' },
              { text: '进阶用法', link: '/zh/guide/advanced' },
            ]
          },
          {
            text: '参考',
            items: [
              { text: 'CLI', link: '/zh/reference/cli' },
              { text: '配置项', link: '/zh/reference/config' },
              { text: '词表格式', link: '/zh/reference/taxonomy' },
            ]
          },
          { text: 'GitHub', link: REPO },
        ],
        sidebar: {
          '/zh/guide/': [
            {
              text: '使用指南',
              items: [
                { text: '安装', link: '/zh/guide/installation' },
                { text: '配置', link: '/zh/guide/configuration' },
                { text: '进阶用法', link: '/zh/guide/advanced' },
              ],
            },
          ],
          '/zh/reference/': [
            {
              text: '参考',
              items: [
                { text: 'CLI', link: '/zh/reference/cli' },
                { text: '配置项', link: '/zh/reference/config' },
                { text: '词表格式', link: '/zh/reference/taxonomy' },
              ],
            },
          ],
        },
        editLink: {
          pattern: `${REPO}/edit/master/docs/:path`,
          text: '在 GitHub 上编辑此页',
        },
        outline: { level: [2, 3], label: '本页内容' },
        docFooter: { prev: '上一页', next: '下一页' },
        lastUpdated: { text: '最后更新' },
        returnToTopLabel: '返回顶部',
        sidebarMenuLabel: '菜单',
        darkModeSwitchLabel: '切换主题',
        footer: {
          message: 'Bookmarks Cleaner · Offline-first bookmark cleanup',
          copyright: `Copyright © 2025-${new Date().getFullYear()} LessUp`,
        },
      },
    },
    en: {
      label: 'English',
      lang: 'en-US',
      link: '/en/',
      title: 'Bookmarks Cleaner',
      description: 'Offline-first bookmark cleaner for developers: rules-first, ML-assisted, LLM-optional.',
      head: meta('en'),
      themeConfig: {
        nav: [
          {
            text: 'Guide',
            items: [
              { text: 'Installation', link: '/en/guide/installation' },
              { text: 'Configuration', link: '/en/guide/configuration' },
              { text: 'Advanced', link: '/en/guide/advanced' },
            ]
          },
          {
            text: 'Reference',
            items: [
              { text: 'CLI', link: '/en/reference/cli' },
              { text: 'Configuration', link: '/en/reference/config' },
              { text: 'Taxonomy', link: '/en/reference/taxonomy' },
            ]
          },
          { text: 'GitHub', link: REPO },
        ],
        sidebar: {
          '/en/guide/': [
            {
              text: 'Guide',
              items: [
                { text: 'Installation', link: '/en/guide/installation' },
                { text: 'Configuration', link: '/en/guide/configuration' },
                { text: 'Advanced', link: '/en/guide/advanced' },
              ],
            },
          ],
          '/en/reference/': [
            {
              text: 'Reference',
              items: [
                { text: 'CLI', link: '/en/reference/cli' },
                { text: 'Configuration', link: '/en/reference/config' },
                { text: 'Taxonomy', link: '/en/reference/taxonomy' },
              ],
            },
          ],
        },
        editLink: {
          pattern: `${REPO}/edit/master/docs/:path`,
          text: 'Edit this page on GitHub',
        },
        outline: { level: [2, 3], label: 'On this page' },
        docFooter: { prev: 'Previous', next: 'Next' },
        lastUpdated: { text: 'Last updated' },
        returnToTopLabel: 'Return to top',
        sidebarMenuLabel: 'Menu',
        darkModeSwitchLabel: 'Appearance',
        footer: {
          message: 'Bookmarks Cleaner · Offline-first bookmark cleanup',
          copyright: `Copyright © 2025-${new Date().getFullYear()} LessUp`,
        },
      },
    },
  },

  themeConfig: {
    search: { provider: 'local' },
    socialLinks: [
      { icon: 'github', link: REPO },
    ],
  },

  vite: {
    build: {
      chunkSizeWarningLimit: 1000,
    },
    plugins: [llmstxt()],
  },
}))
