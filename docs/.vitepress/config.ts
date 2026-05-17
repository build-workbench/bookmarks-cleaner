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
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap' }],
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
    ['script', {}, `
      (function() {
        const key = 'bookmarks-cleaner-lang';
        const base = document.querySelector('base')?.getAttribute('href') || '/';
        const path = location.pathname;
        const isRoot = path === base || path === base + 'index.html' || path === '/' || path === '/index.html';
        if (isRoot) {
          const stored = localStorage.getItem(key);
          const targetLang = stored || (navigator.language || '').toLowerCase().startsWith('zh') ? 'zh' : 'en';
          if (!stored) localStorage.setItem(key, targetLang);
          location.replace(base + targetLang + '/');
        }
      })();
    `],
  ],

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
            text: '白皮书',
            items: [
              { text: '技术白皮书', link: '/zh/whitepaper' },
              { text: '架构决策记录', link: '/zh/adr' },
              { text: '演进思考', link: '/zh/evolution' },
            ]
          },
          {
            text: '架构设计',
            items: [
              { text: 'Pipeline 架构', link: '/zh/architecture/pipeline' },
              { text: '依赖注入容器', link: '/zh/architecture/container' },
              { text: 'Protocol 接口', link: '/zh/architecture/protocols' },
            ]
          },
          {
            text: '算法原理',
            items: [
              { text: '规则引擎', link: '/zh/algorithms/rule-engine' },
              { text: 'ML 分类器', link: '/zh/algorithms/ml-classifier' },
              { text: '融合算法', link: '/zh/algorithms/fusion' },
              { text: 'LLM 集成', link: '/zh/algorithms/llm-integration' },
            ]
          },
          {
            text: '参考',
            items: [
              { text: 'CLI', link: '/zh/reference/cli' },
              { text: '配置项', link: '/zh/reference/config' },
              { text: '词表格式', link: '/zh/reference/taxonomy' },
              { text: 'Python API', link: '/zh/reference/api' },
            ]
          },
          { text: 'GitHub', link: REPO },
        ],
        sidebar: {
          '/zh/whitepaper': [
            { text: '技术白皮书', link: '/zh/whitepaper' },
          ],
          '/zh/adr': [
            { text: '架构决策记录', link: '/zh/adr' },
          ],
          '/zh/evolution': [
            { text: '演进思考', link: '/zh/evolution' },
          ],
          '/zh/guide/': [
            {
              text: '使用指南',
              collapsed: false,
              items: [
                { text: '安装', link: '/zh/guide/installation' },
                { text: '配置', link: '/zh/guide/configuration' },
                { text: '进阶用法', link: '/zh/guide/advanced' },
              ],
            },
          ],
          '/zh/architecture/': [
            {
              text: '架构设计',
              collapsed: false,
              items: [
                { text: 'Pipeline 架构', link: '/zh/architecture/pipeline' },
                { text: '依赖注入容器', link: '/zh/architecture/container' },
                { text: 'Protocol 接口', link: '/zh/architecture/protocols' },
              ],
            },
          ],
          '/zh/algorithms/': [
            {
              text: '算法原理',
              collapsed: false,
              items: [
                { text: '规则引擎', link: '/zh/algorithms/rule-engine' },
                { text: 'ML 分类器', link: '/zh/algorithms/ml-classifier' },
                { text: '语义分析器', link: '/zh/algorithms/semantic-analyzer' },
                { text: 'LLM 集成', link: '/zh/algorithms/llm-integration' },
                { text: '融合算法', link: '/zh/algorithms/fusion' },
              ],
            },
          ],
          '/zh/performance/': [
            {
              text: '性能工程',
              collapsed: false,
              items: [
                { text: '并发处理', link: '/zh/performance/concurrency' },
                { text: '缓存策略', link: '/zh/performance/caching' },
                { text: '优化技巧', link: '/zh/performance/optimization' },
              ],
            },
          ],
          '/zh/reference/': [
            {
              text: 'API 参考',
              collapsed: false,
              items: [
                { text: 'CLI 命令', link: '/zh/reference/cli' },
                { text: '配置项', link: '/zh/reference/config' },
                { text: '词表格式', link: '/zh/reference/taxonomy' },
                { text: 'Python API', link: '/zh/reference/api' },
              ],
            },
          ],
          '/zh/resources/': [
            {
              text: '学术资源',
              collapsed: false,
              items: [
                { text: '参考文献', link: '/zh/resources/references' },
                { text: '相关项目', link: '/zh/resources/related-projects' },
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
          copyright: `Copyright \u00A9 2025-${new Date().getFullYear()} LessUp`,
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
            text: 'Whitepaper',
            items: [
              { text: 'Technical Whitepaper', link: '/en/whitepaper' },
              { text: 'Architecture Decisions', link: '/en/adr' },
              { text: 'Evolution', link: '/en/evolution' },
            ]
          },
          {
            text: 'Architecture',
            items: [
              { text: 'Pipeline', link: '/en/architecture/pipeline' },
              { text: 'DI Container', link: '/en/architecture/container' },
              { text: 'Protocols', link: '/en/architecture/protocols' },
            ]
          },
          {
            text: 'Algorithms',
            items: [
              { text: 'Rule Engine', link: '/en/algorithms/rule-engine' },
              { text: 'ML Classifier', link: '/en/algorithms/ml-classifier' },
              { text: 'Fusion', link: '/en/algorithms/fusion' },
              { text: 'LLM Integration', link: '/en/algorithms/llm-integration' },
            ]
          },
          {
            text: 'Reference',
            items: [
              { text: 'CLI', link: '/en/reference/cli' },
              { text: 'Configuration', link: '/en/reference/config' },
              { text: 'Taxonomy', link: '/en/reference/taxonomy' },
              { text: 'Python API', link: '/en/reference/api' },
            ]
          },
          { text: 'GitHub', link: REPO },
        ],
        sidebar: {
          '/en/whitepaper': [
            { text: 'Technical Whitepaper', link: '/en/whitepaper' },
          ],
          '/en/adr': [
            { text: 'Architecture Decisions', link: '/en/adr' },
          ],
          '/en/evolution': [
            { text: 'Evolution', link: '/en/evolution' },
          ],
          '/en/guide/': [
            {
              text: 'Guide',
              collapsed: false,
              items: [
                { text: 'Installation', link: '/en/guide/installation' },
                { text: 'Configuration', link: '/en/guide/configuration' },
                { text: 'Advanced', link: '/en/guide/advanced' },
              ],
            },
          ],
          '/en/architecture/': [
            {
              text: 'Architecture',
              collapsed: false,
              items: [
                { text: 'Pipeline', link: '/en/architecture/pipeline' },
                { text: 'DI Container', link: '/en/architecture/container' },
                { text: 'Protocols', link: '/en/architecture/protocols' },
              ],
            },
          ],
          '/en/algorithms/': [
            {
              text: 'Algorithms',
              collapsed: false,
              items: [
                { text: 'Rule Engine', link: '/en/algorithms/rule-engine' },
                { text: 'ML Classifier', link: '/en/algorithms/ml-classifier' },
                { text: 'Semantic Analyzer', link: '/en/algorithms/semantic-analyzer' },
                { text: 'LLM Integration', link: '/en/algorithms/llm-integration' },
                { text: 'Fusion', link: '/en/algorithms/fusion' },
              ],
            },
          ],
          '/en/performance/': [
            {
              text: 'Performance Engineering',
              collapsed: false,
              items: [
                { text: 'Concurrency', link: '/en/performance/concurrency' },
                { text: 'Caching', link: '/en/performance/caching' },
                { text: 'Optimization', link: '/en/performance/optimization' },
              ],
            },
          ],
          '/en/reference/': [
            {
              text: 'API Reference',
              collapsed: false,
              items: [
                { text: 'CLI', link: '/en/reference/cli' },
                { text: 'Configuration', link: '/en/reference/config' },
                { text: 'Taxonomy', link: '/en/reference/taxonomy' },
                { text: 'Python API', link: '/en/reference/api' },
              ],
            },
          ],
          '/en/resources/': [
            {
              text: 'Academic Resources',
              collapsed: false,
              items: [
                { text: 'References', link: '/en/resources/references' },
                { text: 'Related Projects', link: '/en/resources/related-projects' },
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
          message: 'Bookmarks Cleaner \u00B7 Offline-first bookmark cleanup',
          copyright: `Copyright \u00A9 2025-${new Date().getFullYear()} LessUp`,
        },
      },
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
