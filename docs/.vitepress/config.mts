import { defineConfig } from 'vitepress'

// Site metadata
const SITE = {
  title: 'CleanBook',
  description: '开发者的智能书签整理工具 - 规则优先，ML辅助，LLM可选，离线可用',
  descriptionEn: 'Smart bookmark cleaner for developers - Rules-first, ML-assisted, LLM-optional, offline-ready',
  version: '2.0.0',
  repo: 'https://github.com/LessUp/bookmarks-cleaner',
  docsRepo: 'https://github.com/LessUp/bookmarks-cleaner',
}

// Generate meta tags for SEO
function generateMetaTags(lang: 'zh' | 'en') {
  const isZh = lang === 'zh'
  const description = isZh ? SITE.description : SITE.descriptionEn
  const title = isZh ? 'CleanBook - 智能书签清理工具' : 'CleanBook - Smart Bookmark Cleaner'
  const locale = isZh ? 'zh_CN' : 'en_US'
  const keywords = isZh
    ? '书签管理,书签清理,AI分类,浏览器工具,Python,CLI,开源,离线处理'
    : 'bookmark manager,bookmark cleaner,AI classification,browser tool,Python,CLI,open source,offline processing'

  return [
    ['meta', { name: 'description', content: description }],
    ['meta', { name: 'keywords', content: keywords }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: title }],
    ['meta', { property: 'og:description', content: description }],
    ['meta', { property: 'og:locale', content: locale }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:title', content: title }],
    ['meta', { name: 'twitter:description', content: description }],
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ['link', { rel: 'manifest', href: '/manifest.json' }],
    ['meta', { name: 'theme-color', content: '#3b82f6' }],
  ]
}

// Chinese navigation
const zhNav = [
  { text: '快速开始', link: '/zh/quickstart' },
  { text: '使用指南', link: '/zh/guide/installation' },
  { text: '配置参考', link: '/zh/reference/config' },
  { text: 'GitHub', link: SITE.repo },
]

// English navigation
const enNav = [
  { text: 'Quick Start', link: '/en/quickstart' },
  { text: 'Guide', link: '/en/guide/installation' },
  { text: 'Reference', link: '/en/reference/config' },
  { text: 'GitHub', link: SITE.repo },
]

// Chinese sidebar
const zhSidebar = {
  '/zh/guide/': [
    {
      text: '使用指南',
      items: [
        { text: '安装', link: '/zh/guide/installation' },
        { text: '快速开始', link: '/zh/quickstart' },
        { text: '配置详解', link: '/zh/guide/configuration' },
        { text: '最佳实践', link: '/zh/guide/best-practices' },
      ],
    },
    {
      text: '示例',
      items: [
        { text: '基础用法', link: '/zh/examples/basic' },
        { text: '自定义规则', link: '/zh/examples/custom-rules' },
        { text: '团队配置', link: '/zh/examples/team' },
      ],
    },
  ],
  '/zh/reference/': [
    {
      text: '配置参考',
      items: [
        { text: '配置项说明', link: '/zh/reference/config' },
        { text: '词表格式', link: '/zh/reference/taxonomy' },
        { text: 'LLM 提示词', link: '/zh/reference/llm-prompts' },
      ],
    },
    {
      text: '架构设计',
      items: [
        { text: '设计概述', link: '/zh/design/overview' },
        { text: '系统架构', link: '/zh/design/architecture' },
        { text: 'ML 设计', link: '/zh/design/ml-design' },
      ],
    },
  ],
}

// English sidebar
const enSidebar = {
  '/en/guide/': [
    {
      text: 'Guide',
      items: [
        { text: 'Installation', link: '/en/guide/installation' },
        { text: 'Quick Start', link: '/en/quickstart' },
        { text: 'Configuration', link: '/en/guide/configuration' },
        { text: 'Best Practices', link: '/en/guide/best-practices' },
      ],
    },
    {
      text: 'Examples',
      items: [
        { text: 'Basic Usage', link: '/en/examples/basic' },
        { text: 'Custom Rules', link: '/en/examples/custom-rules' },
        { text: 'Team Setup', link: '/en/examples/team' },
      ],
    },
  ],
  '/en/reference/': [
    {
      text: 'Reference',
      items: [
        { text: 'Configuration', link: '/en/reference/config' },
        { text: 'Taxonomy Format', link: '/en/reference/taxonomy' },
        { text: 'LLM Prompts', link: '/en/reference/llm-prompts' },
      ],
    },
    {
      text: 'Design',
      items: [
        { text: 'Overview', link: '/en/design/overview' },
        { text: 'Architecture', link: '/en/design/architecture' },
        { text: 'ML Design', link: '/en/design/ml-design' },
      ],
    },
  ],
}

export default defineConfig({
  // Site config
  base: '/bookmarks-cleaner/',
  lang: 'zh-CN',
  title: SITE.title,
  description: SITE.description,
  
  // Clean URLs
  cleanUrls: true,
  
  // Last updated
  lastUpdated: true,

  // Head
  head: generateMetaTags('zh'),

  // Multi-language locales
  locales: {
    root: {
      label: '简体中文',
      lang: 'zh-CN',
      title: SITE.title,
      description: SITE.description,
      head: generateMetaTags('zh'),
      themeConfig: {
        nav: zhNav,
        sidebar: zhSidebar,
        editLink: {
          pattern: `${SITE.docsRepo}/edit/master/docs/:path`,
          text: '在 GitHub 上编辑此页',
        },
        outline: {
          level: [2, 3],
          label: '本页内容',
        },
        docFooter: {
          prev: '上一页',
          next: '下一页',
        },
        lastUpdated: {
          text: '最后更新',
        },
        returnToTopLabel: '返回顶部',
        sidebarMenuLabel: '菜单',
        darkModeSwitchLabel: '切换主题',
        footer: {
          message: '基于 MIT 许可发布',
          copyright: `Copyright © 2025-${new Date().getFullYear()} LessUp`,
        },
      },
    },
    en: {
      label: 'English',
      lang: 'en-US',
      title: SITE.title,
      description: SITE.descriptionEn,
      head: generateMetaTags('en'),
      themeConfig: {
        nav: enNav,
        sidebar: enSidebar,
        editLink: {
          pattern: `${SITE.docsRepo}/edit/master/docs/:path`,
          text: 'Edit this page on GitHub',
        },
        outline: {
          level: [2, 3],
          label: 'On this page',
        },
        docFooter: {
          prev: 'Previous',
          next: 'Next',
        },
        lastUpdated: {
          text: 'Last updated',
        },
        returnToTopLabel: 'Return to top',
        sidebarMenuLabel: 'Menu',
        darkModeSwitchLabel: 'Appearance',
        footer: {
          message: 'Released under MIT License',
          copyright: `Copyright © 2025-${new Date().getFullYear()} LessUp`,
        },
      },
    },
  },

  // Theme config
  themeConfig: {
    logo: { src: '/logo.svg', alt: 'CleanBook' },
    siteTitle: SITE.title,
    socialLinks: [{ icon: 'github', link: SITE.repo }],
    
    // Search
    search: {
      provider: 'local',
      options: {
        detailedView: true,
        translations: {
          button: { buttonText: '搜索', buttonAriaLabel: '搜索文档' },
          modal: {
            noResultsText: '未找到相关结果',
            resetButtonTitle: '清除搜索',
            footer: {
              selectText: '选择',
              navigateText: '切换',
              closeText: '关闭',
            },
          },
        },
      },
    },
  },

  // Markdown
  markdown: {
    lineNumbers: true,
  },

  // Vite
  vite: {
    build: {
      chunkSizeWarningLimit: 1000,
    },
  },
})
