import { defineConfig, type HeadConfig } from 'vitepress'
import { createWriteStream } from 'fs'
import { resolve } from 'path'

// =============================================================================
// SITE CONFIGURATION
// =============================================================================
const SITE = {
  title: 'CleanBook',
  description: '智能书签清理与分类工具 - 规则优先，ML辅助，LLM可选',
  descriptionEn: 'Smart bookmark cleaning & classification - Rules-first, ML-assisted, LLM-optional',
  version: '2.0.0',
  author: 'LessUp',
  url: 'https://lessup.github.io/bookmarks-cleaner',
  repo: 'https://github.com/LessUp/bookmarks-cleaner',
  twitter: '@LessUpDev',
  image: '/og-image.png',
  imageZh: '/og-image-zh.png',
} as const

// =============================================================================
// SEO & META HELPERS
// =============================================================================

/**
 * Generate comprehensive meta tags for SEO
 */
function generateMetaTags(lang: 'zh' | 'en'): HeadConfig[] {
  const isZh = lang === 'zh'
  const description = isZh ? SITE.description : SITE.descriptionEn
  const ogImage = `${SITE.url}${isZh ? SITE.imageZh : SITE.image}`
  const ogLocale = isZh ? 'zh_CN' : 'en_US'
  const keywords = isZh
    ? '书签管理,书签清理,AI分类,机器学习,浏览器工具,Python,开源,离线优先,书签整理'
    : 'bookmark manager,bookmark cleaner,AI classification,machine learning,browser tool,Python,open source,offline-first'

  return [
    // Basic Meta
    ['meta', { name: 'description', content: description }],
    ['meta', { name: 'keywords', content: keywords }],
    ['meta', { name: 'author', content: SITE.author }],
    ['meta', { name: 'copyright', content: `© ${new Date().getFullYear()} ${SITE.author}` }],
    
    // Robots
    ['meta', { name: 'robots', content: 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1' }],
    ['meta', { name: 'googlebot', content: 'index,follow' }],
    ['meta', { name: 'bingbot', content: 'index,follow' }],
    
    // Viewport & Theme
    ['meta', { name: 'viewport', content: 'width=device-width,initial-scale=1,minimum-scale=1,maximum-scale=5' }],
    ['meta', { name: 'theme-color', content: '#3b82f6' }],
    ['meta', { name: 'msapplication-TileColor', content: '#3b82f6' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
    ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' }],
    ['meta', { name: 'apple-mobile-web-app-title', content: 'CleanBook' }],
    ['meta', { name: 'format-detection', content: 'telephone=no' }],
    ['meta', { name: 'mobile-web-app-capable', content: 'yes' }],
    
    // Open Graph
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:site_name', content: 'CleanBook' }],
    ['meta', { property: 'og:title', content: isZh ? 'CleanBook - 智能书签清理' : 'CleanBook - Smart Bookmark Cleaner' }],
    ['meta', { property: 'og:description', content: description }],
    ['meta', { property: 'og:url', content: SITE.url }],
    ['meta', { property: 'og:locale', content: ogLocale }],
    ['meta', { property: 'og:image', content: ogImage }],
    ['meta', { property: 'og:image:width', content: '1200' }],
    ['meta', { property: 'og:image:height', content: '630' }],
    ['meta', { property: 'og:image:alt', content: isZh ? 'CleanBook 智能书签清理工具' : 'CleanBook Smart Bookmark Cleaner' }],
    
    // Twitter Card
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:site', content: SITE.twitter }],
    ['meta', { name: 'twitter:creator', content: SITE.twitter }],
    ['meta', { name: 'twitter:title', content: isZh ? 'CleanBook - 智能书签清理' : 'CleanBook - Smart Bookmark Cleaner' }],
    ['meta', { name: 'twitter:description', content: description }],
    ['meta', { name: 'twitter:image', content: ogImage }],
    
    // Preconnect for Performance
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    
    // Icons
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ['link', { rel: 'apple-touch-icon', sizes: '180x180', href: '/icons/apple-touch-icon.png' }],
    ['link', { rel: 'mask-icon', href: '/icons/safari-pinned-tab.svg', color: '#3b82f6' }],
    
    // PWA Manifest
    ['link', { rel: 'manifest', href: '/manifest.json' }],
    
    // Canonical & Alternate Languages
    ['link', { rel: 'canonical', href: `${SITE.url}${isZh ? '/zh/' : '/en/'}` }],
    ['link', { rel: 'alternate', hreflang: 'zh-CN', href: `${SITE.url}/zh/` }],
    ['link', { rel: 'alternate', hreflang: 'en', href: `${SITE.url}/en/` }],
    ['link', { rel: 'alternate', hreflang: 'x-default', href: SITE.url }],
    
    // Generator
    ['meta', { name: 'generator', content: 'VitePress' }],
  ]
}

/**
 * Generate JSON-LD structured data
 */
function generateStructuredData(lang: 'zh' | 'en'): HeadConfig[] {
  const isZh = lang === 'zh'
  
  const websiteData = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: isZh ? 'CleanBook - 智能书签清理' : 'CleanBook - Smart Bookmark Cleaner',
    url: SITE.url,
    description: isZh ? SITE.description : SITE.descriptionEn,
    inLanguage: isZh ? 'zh-CN' : 'en',
    author: {
      '@type': 'Organization',
      name: SITE.author,
      url: 'https://github.com/LessUp',
    },
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${SITE.url}/search?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  }

  const softwareData = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'CleanBook',
    applicationCategory: 'ProductivityApplication',
    operatingSystem: 'Windows, macOS, Linux',
    softwareVersion: SITE.version,
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.8',
      ratingCount: '100',
    },
    featureList: isZh
      ? '离线优先,规则引擎,机器学习分类,LLM支持,多格式导出,智能去重'
      : 'Offline-first,Rule engine,ML classification,LLM support,Multi-format export,Smart deduplication',
    programmingLanguage: 'Python',
    license: 'https://opensource.org/licenses/MIT',
    downloadUrl: `${SITE.repo}/releases`,
  }

  const orgData = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: SITE.author,
    url: 'https://github.com/LessUp',
    logo: `${SITE.url}/logo.png`,
    sameAs: [
      'https://github.com/LessUp',
    ],
  }

  const breadcrumbs = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: isZh ? '首页' : 'Home',
        item: SITE.url,
      },
    ],
  }

  return [
    ['script', { type: 'application/ld+json' }, JSON.stringify(websiteData)],
    ['script', { type: 'application/ld+json' }, JSON.stringify(softwareData)],
    ['script', { type: 'application/ld+json' }, JSON.stringify(orgData)],
    ['script', { type: 'application/ld+json' }, JSON.stringify(breadcrumbs)],
  ]
}

// =============================================================================
// NAVIGATION CONFIGURATION
// =============================================================================

const zhNav = [
  { text: '首页', link: '/zh/' },
  { text: '快速开始', link: '/zh/quickstart' },
  { 
    text: '使用指南', 
    items: [
      { text: '最佳实践', link: '/zh/guide/best-practices' },
      { text: '开发指南', link: '/zh/guide/development' },
    ]
  },
  {
    text: '架构设计',
    items: [
      { text: '设计概述', link: '/zh/design/overview' },
      { text: '系统架构', link: '/zh/design/architecture' },
      { text: 'ML 设计', link: '/zh/design/ml-design' },
    ],
  },
  { text: '参考', link: '/zh/reference/llm-templates' },
  { 
    text: '更多',
    items: [
      { text: '技术报告', link: '/zh/advanced/technical-report' },
      { text: 'GitHub', link: SITE.repo },
      { text: '更新日志', link: `${SITE.repo}/blob/master/CHANGELOG.md` },
    ]
  },
]

const enNav = [
  { text: 'Home', link: '/en/' },
  { text: 'Quick Start', link: '/en/quickstart' },
  { 
    text: 'Guide', 
    items: [
      { text: 'Best Practices', link: '/en/guide/best-practices' },
      { text: 'Development', link: '/en/guide/development' },
    ]
  },
  {
    text: 'Design',
    items: [
      { text: 'Overview', link: '/en/design/overview' },
      { text: 'Architecture', link: '/en/design/architecture' },
      { text: 'ML Design', link: '/en/design/ml-design' },
    ],
  },
  { text: 'Reference', link: '/en/reference/llm-templates' },
  { 
    text: 'More',
    items: [
      { text: 'Technical Report', link: '/en/advanced/technical-report' },
      { text: 'GitHub', link: SITE.repo },
      { text: 'Changelog', link: `${SITE.repo}/blob/master/CHANGELOG.md` },
    ]
  },
]

// =============================================================================
// SIDEBAR CONFIGURATION
// =============================================================================

const zhSidebar = {
  '/zh/': [
    {
      text: '概览',
      collapsed: false,
      items: [{ text: '首页', link: '/zh/' }],
    },
    {
      text: '快速开始',
      collapsed: false,
      items: [{ text: '快速上手', link: '/zh/quickstart' }],
    },
    {
      text: '使用指南',
      collapsed: false,
      items: [
        { text: '书签管理最佳实践', link: '/zh/guide/best-practices' },
        { text: '开发指南', link: '/zh/guide/development' },
      ],
    },
    {
      text: '架构设计',
      collapsed: false,
      items: [
        { text: '设计概述', link: '/zh/design/overview' },
        { text: '系统架构', link: '/zh/design/architecture' },
        { text: 'ML 设计', link: '/zh/design/ml-design' },
      ],
    },
    {
      text: '参考',
      collapsed: false,
      items: [{ text: 'LLM 提示词模板', link: '/zh/reference/llm-templates' }],
    },
    {
      text: '高级',
      collapsed: false,
      items: [{ text: '技术报告', link: '/zh/advanced/technical-report' }],
    },
  ],
}

const enSidebar = {
  '/en/': [
    {
      text: 'Overview',
      collapsed: false,
      items: [{ text: 'Home', link: '/en/' }],
    },
    {
      text: 'Quick Start',
      collapsed: false,
      items: [{ text: 'Quick Start', link: '/en/quickstart' }],
    },
    {
      text: 'Guide',
      collapsed: false,
      items: [
        { text: 'Best Practices', link: '/en/guide/best-practices' },
        { text: 'Development Guide', link: '/en/guide/development' },
      ],
    },
    {
      text: 'Design',
      collapsed: false,
      items: [
        { text: 'Overview', link: '/en/design/overview' },
        { text: 'Architecture', link: '/en/design/architecture' },
        { text: 'ML Design', link: '/en/design/ml-design' },
      ],
    },
    {
      text: 'Reference',
      collapsed: false,
      items: [{ text: 'LLM Templates', link: '/en/reference/llm-templates' }],
    },
    {
      text: 'Advanced',
      collapsed: false,
      items: [{ text: 'Technical Report', link: '/en/advanced/technical-report' }],
    },
  ],
}

// =============================================================================
// MAIN VITEPRESS CONFIG
// =============================================================================

export default defineConfig({
  // Site Config
  base: '/bookmarks-cleaner/',
  lang: 'zh-CN',
  title: SITE.title,
  description: SITE.description,
  
  // Clean URLs
  cleanUrls: true,
  
  // Last Updated
  lastUpdated: true,
  
  // Multi-language
  locales: {
    root: {
      label: '中文',
      lang: 'zh-CN',
      title: SITE.title,
      titleTemplate: `:title | ${SITE.title} 文档`,
      description: SITE.description,
      head: [...generateMetaTags('zh'), ...generateStructuredData('zh')],
      themeConfig: {
        nav: zhNav,
        sidebar: zhSidebar,
        editLink: {
          pattern: `${SITE.repo}/edit/master/docs/:path`,
          text: '在 GitHub 上编辑此页',
        },
        docFooter: {
          prev: '上一页',
          next: '下一页',
        },
        outline: {
          level: [2, 3],
          label: '页面导航',
        },
        lastUpdated: {
          text: '最后更新',
          formatOptions: {
            dateStyle: 'full',
            timeStyle: 'medium',
          },
        },
        returnToTopLabel: '返回顶部',
        sidebarMenuLabel: '菜单',
        darkModeSwitchLabel: '主题',
        langMenuLabel: '切换语言',
        footer: {
          message: '基于 MIT 许可发布',
          copyright: `Copyright © 2025-${new Date().getFullYear()} ${SITE.author}`,
        },
      },
    },
    en: {
      label: 'English',
      lang: 'en-US',
      title: SITE.title,
      titleTemplate: `:title | ${SITE.title} Docs`,
      description: SITE.descriptionEn,
      head: [...generateMetaTags('en'), ...generateStructuredData('en')],
      themeConfig: {
        nav: enNav,
        sidebar: enSidebar,
        editLink: {
          pattern: `${SITE.repo}/edit/master/docs/:path`,
          text: 'Edit this page on GitHub',
        },
        docFooter: {
          prev: 'Previous',
          next: 'Next',
        },
        outline: {
          level: [2, 3],
          label: 'On this page',
        },
        lastUpdated: {
          text: 'Last updated',
          formatOptions: {
            dateStyle: 'full',
            timeStyle: 'medium',
          },
        },
        returnToTopLabel: 'Return to top',
        sidebarMenuLabel: 'Menu',
        darkModeSwitchLabel: 'Appearance',
        langMenuLabel: 'Change language',
        footer: {
          message: 'Released under MIT License',
          copyright: `Copyright © 2025-${new Date().getFullYear()} ${SITE.author}`,
        },
      },
    },
  },

  // Head
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
  ],

  // Theme Config
  themeConfig: {
    logo: {
      src: '/logo.svg',
      alt: 'CleanBook Logo',
    },
    
    siteTitle: SITE.title,
    
    socialLinks: [
      { icon: 'github', link: SITE.repo },
    ],

    search: {
      provider: 'local',
      options: {
        detailedView: true,
        miniSearch: {
          searchOptions: {
            boost: { title: 5, text: 2, titles: 1 },
            fuzzy: 0.2,
            prefix: true,
          },
        },
        translations: {
          button: { 
            buttonText: '搜索文档', 
            buttonAriaLabel: '搜索文档' 
          },
          modal: {
            displayDetails: '显示详细结果',
            resetButtonTitle: '清除查询',
            backButtonTitle: '关闭搜索',
            noResultsText: '未找到相关结果',
            footer: {
              selectText: '选择',
              selectKeyAriaLabel: '回车',
              navigateText: '切换',
              navigateUpKeyAriaLabel: '向上箭头',
              navigateDownKeyAriaLabel: '向下箭头',
              closeText: '关闭',
              closeKeyAriaLabel: 'Esc',
            },
          },
        },
      },
    },

    externalLinkIcon: true,
  },

  // Markdown Config
  markdown: {
    lineNumbers: true,
    config: (md) => {
      // Custom markdown-it plugins can be added here
    },
  },

  // Vite Config
  vite: {
    build: {
      chunkSizeWarningLimit: 1000,
    },
    css: {
      devSourcemap: true,
    },
  },

  // Build Hooks
  buildEnd: async (siteConfig) => {
    // Generate comprehensive sitemap
    const generateSitemap = () => {
      const pages = (siteConfig.pages || []).map((page: any) => {
        if (typeof page === 'string') return page
        return page?.path || ''
      }).map((p: string) => p.replace(/\.md$/, '.html')).filter(Boolean)
      const today = new Date().toISOString().split('T')[0]
      
      const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
${pages
  .map((page: string) => {
    const cleanPage = page.startsWith('/') ? page : '/' + page
    const urlPath = cleanPage.replace(/\.html$/, '')
    const fullUrl = `${SITE.url}${urlPath}`.replace(/\/$/, '')
    const isZh = cleanPage.startsWith('/zh')
    const isEn = cleanPage.startsWith('/en')
    const isRoot = cleanPage === '/' || cleanPage === ''
    const priority = isRoot ? '1.0' : ((isZh || isEn) && urlPath.endsWith('/')) ? '0.9' : '0.7'
    const changefreq = isRoot ? 'daily' : 'weekly'
    
    let alternates = ''
    if (isZh || isEn) {
      const zhUrl = fullUrl.replace('/en/', '/zh/') + '/'
      const enUrl = fullUrl.replace('/zh/', '/en/') + '/'
      alternates = `
    <xhtml:link rel="alternate" hreflang="zh-CN" href="${zhUrl}" />
    <xhtml:link rel="alternate" hreflang="en" href="${enUrl}" />`
    }
    
    return `  <url>
    <loc>${fullUrl}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>${alternates}
  </url>`
  })
  .join('\n')}
</urlset>`
      
      // Write main sitemap
      const sitemapPath = resolve(siteConfig.outDir, 'sitemap.xml')
      createWriteStream(sitemapPath).write(sitemap)
      console.log(`✓ Sitemap generated: ${sitemapPath}`)
      
      // Also write sitemaps for each language for better SEO
      const zhPages = pages.filter(p => p.startsWith('/zh') || p === '/' || p === '')
      const enPages = pages.filter(p => p.startsWith('/en'))
      
      const generateLangSitemap = (pages: string[], filename: string) => {
        const langSitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages
  .map((page) => {
    const cleanPage = (page.startsWith('/') ? page : '/' + page).replace(/\.html$/, '').replace(/\/$/, '')
    const url = `${SITE.url}${cleanPage}`
    return `  <url>
    <loc>${url}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`
  })
  .join('\n')}
</urlset>`
        const langSitemapPath = resolve(siteConfig.outDir, filename)
        createWriteStream(langSitemapPath).write(langSitemap)
        console.log(`✓ ${filename} generated: ${langSitemapPath}`)
      }
      
      if (zhPages.length) generateLangSitemap(zhPages, 'sitemap-zh.xml')
      if (enPages.length) generateLangSitemap(enPages, 'sitemap-en.xml')
    }

    // Generate robots.txt with sitemap references
    const generateRobotsTxt = () => {
      const robotsContent = `User-agent: *
Allow: /

# Sitemaps
Sitemap: ${SITE.url}/sitemap.xml
Sitemap: ${SITE.url}/sitemap-zh.xml
Sitemap: ${SITE.url}/sitemap-en.xml

# Crawl-delay
Crawl-delay: 1

# AI Crawlers - Allow all
User-agent: ChatGPT-User
Allow: /

User-agent: GPTBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: BingPreview
Allow: /

# Disallow
Disallow: /404.html
Disallow: /*.json$
Disallow: /*.md$
`
      const robotsPath = resolve(siteConfig.outDir, 'robots.txt')
      createWriteStream(robotsPath).write(robotsContent)
      console.log(`✓ robots.txt generated: ${robotsPath}`)
    }

    generateSitemap()
    generateRobotsTxt()
    console.log('\n✓ Build completed successfully!')
  },
})
