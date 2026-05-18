import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import llmstxt from 'vitepress-plugin-llms'
import { createLocaleThemeConfig, localeRedirectScript } from './shared/site-data.mjs'

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
    ? '书签清理,书签分类,离线工具,Python CLI,规则引擎,机器学习,文本分类,集成学习'
    : 'bookmark cleaner,bookmark classification,offline tool,Python CLI,rules engine,machine learning,text classification,ensemble learning'

  return [
    ['meta', { name: 'description', content: description }],
    ['meta', { name: 'keywords', content: keywords }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'Bookmarks Cleaner' }],
    ['meta', { property: 'og:description', content: description }],
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ['link', { rel: 'manifest', href: '/manifest.json' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Manrope:wght@400;500;600;700;800&display=swap' }],
  ]
}

export default withMermaid(defineConfig({
  base,
  title: 'Bookmarks Cleaner',
  description: 'Offline-first bookmark cleaner for developers',
  lastUpdated: true,

  head: [
    ['meta', { name: 'theme-color', content: '#0066FF' }],
    ['meta', { name: 'theme-color', content: '#4D94FF', media: '(prefers-color-scheme: dark)' }],
    ['script', {}, localeRedirectScript],
  ],

  locales: {
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      link: '/zh/',
      title: 'Bookmarks Cleaner',
      description: '开发者的离线优先书签清理与分类工具：规则优先，ML 辅助，LLM 可选。',
      head: meta('zh'),
      themeConfig: createLocaleThemeConfig('zh'),
    },
    en: {
      label: 'English',
      lang: 'en-US',
      link: '/en/',
      title: 'Bookmarks Cleaner',
      description: 'Offline-first bookmark cleaner for developers: rules-first, ML-assisted, LLM-optional.',
      head: meta('en'),
      themeConfig: createLocaleThemeConfig('en'),
    },
  },

  themeConfig: {
    search: { provider: 'local' },
    socialLinks: [
      { icon: 'github', link: REPO },
    ],
    logo: '/logo.svg',
    siteTitle: 'Bookmarks Cleaner',
  },

  mermaid: {
    theme: 'default',
    flowchart: {
      curve: 'basis',
      padding: 20,
    },
  },

  markdown: {
    theme: {
      light: 'github-light',
      dark: 'one-dark-pro',
    },
    lineNumbers: false,
    math: true,
  },

  vite: {
    build: {
      chunkSizeWarningLimit: 1000,
    },
    plugins: [llmstxt()],
  },
}))
