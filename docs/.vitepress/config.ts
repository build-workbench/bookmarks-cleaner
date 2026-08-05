import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import llmstxt from 'vitepress-plugin-llms'
import { createMermaidConfig } from './shared/mermaid-theme.mjs'
import { createThemeConfig } from './shared/site-data.mjs'

const rawBase = process.env.VITEPRESS_BASE
const base = rawBase
  ? rawBase.startsWith('/')
    ? rawBase.endsWith('/') ? rawBase : `${rawBase}/`
    : `/${rawBase}/`
  : '/bookmarks-cleaner/' // Default to production base path for local builds

const REPO = 'https://github.com/LessUp/bookmarks-cleaner'
const SITE_URL = 'https://lessup.github.io'

const description = '开发者的离线优先书签清理与分类工具：规则优先，ML 辅助，LLM 可选。'
const keywords = '书签清理,书签分类,离线工具,Python CLI,规则引擎,机器学习,文本分类,集成学习'

export default withMermaid(defineConfig({
  base,
  lang: 'zh-CN',
  title: 'Bookmarks Cleaner',
  description,
  lastUpdated: true,
  sitemap: {
    hostname: `${SITE_URL}${base}`,
  },

  head: [
    ['meta', { name: 'theme-color', content: '#0066FF' }],
    ['meta', { name: 'theme-color', content: '#4D94FF', media: '(prefers-color-scheme: dark)' }],
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
  ],

  themeConfig: {
    ...createThemeConfig(),
    search: { provider: 'local' },
    socialLinks: [
      { icon: 'github', link: REPO },
    ],
    logo: {
      light: '/logo.svg',
      dark: '/logo-dark.svg',
    },
    siteTitle: 'Bookmarks Cleaner',
  },

  mermaid: createMermaidConfig(),

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
