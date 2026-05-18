const REPO = 'https://github.com/LessUp/bookmarks-cleaner'

const footerMessage = 'Bookmarks Cleaner · Offline-first bookmark cleanup'

const localeText = {
  zh: {
    nav: ['导读', '架构', '算法', '性能', '白皮书', '参考'],
    sidebar: {
      overview: '导读',
      home: '首页',
      installation: '安装',
      configuration: '配置',
      advanced: '进阶用法',
      architecture: '架构',
      pipeline: 'Pipeline 架构',
      container: '依赖注入容器',
      protocols: 'Protocol 接口',
      algorithms: '算法',
      ruleEngine: '规则引擎',
      mlClassifier: 'ML 分类器',
      semanticAnalyzer: '语义分析器',
      llmIntegration: 'LLM 集成',
      fusion: '融合算法',
      performance: '性能',
      concurrency: '并发处理',
      caching: '缓存策略',
      optimization: '优化技巧',
      whitepaper: '白皮书',
      whitepaperDoc: '技术白皮书',
      evolution: '演进思考',
      adr: '架构决策记录',
      references: '参考',
      referencesDoc: '参考文献',
      relatedProjects: '相关项目研究',
      referenceDocs: '参考手册',
      cli: 'CLI 命令',
      config: '配置项',
      taxonomy: '词表格式',
      engineering: '工程实践',
      testingStrategy: '测试策略',
      ciCd: 'CI/CD 配置',
    },
    editLink: '在 GitHub 上编辑此页',
    outline: '本页内容',
    prev: '上一页',
    next: '下一页',
    lastUpdated: '最后更新',
    returnToTop: '返回顶部',
    sidebarMenu: '菜单',
    darkModeSwitch: '切换主题',
  },
  en: {
    nav: ['Overview', 'Architecture', 'Algorithms', 'Performance', 'Whitepaper', 'References'],
    sidebar: {
      overview: 'Overview',
      home: 'Home',
      installation: 'Installation',
      configuration: 'Configuration',
      advanced: 'Advanced',
      architecture: 'Architecture',
      pipeline: 'Pipeline',
      container: 'DI Container',
      protocols: 'Protocols',
      algorithms: 'Algorithms',
      ruleEngine: 'Rule Engine',
      mlClassifier: 'ML Classifier',
      semanticAnalyzer: 'Semantic Analyzer',
      llmIntegration: 'LLM Integration',
      fusion: 'Fusion',
      performance: 'Performance',
      concurrency: 'Concurrency',
      caching: 'Caching',
      optimization: 'Optimization',
      whitepaper: 'Whitepaper',
      whitepaperDoc: 'Technical Whitepaper',
      evolution: 'Evolution',
      adr: 'Architecture Decisions',
      references: 'References',
      referencesDoc: 'References',
      relatedProjects: 'Related Projects',
      referenceDocs: 'Reference',
      cli: 'CLI',
      config: 'Configuration',
      taxonomy: 'Taxonomy',
      engineering: 'Engineering',
      testingStrategy: 'Testing Strategy',
      ciCd: 'CI/CD',
    },
    editLink: 'Edit this page on GitHub',
    outline: 'On this page',
    prev: 'Previous',
    next: 'Next',
    lastUpdated: 'Last updated',
    returnToTop: 'Return to top',
    sidebarMenu: 'Menu',
    darkModeSwitch: 'Appearance',
  },
}

function pathFor(lang, suffix = '') {
  return suffix ? `/${lang}/${suffix}` : `/${lang}/`
}

function themeNav(lang) {
  const copy = localeText[lang]

  return [
    { text: copy.nav[0], link: pathFor(lang) },
    { text: copy.nav[1], link: pathFor(lang, 'architecture/pipeline') },
    { text: copy.nav[2], link: pathFor(lang, 'algorithms/fusion') },
    { text: copy.nav[3], link: pathFor(lang, 'performance/optimization') },
    { text: copy.nav[4], link: pathFor(lang, 'whitepaper') },
    { text: copy.nav[5], link: pathFor(lang, 'resources/references') },
    { text: 'GitHub', link: REPO },
  ]
}

function themeSidebar(lang) {
  const copy = localeText[lang].sidebar
  const base = `/${lang}/`

  return {
    [base]: [
      {
        text: copy.overview,
        collapsed: false,
        items: [
          { text: copy.home, link: base },
          { text: copy.installation, link: pathFor(lang, 'guide/installation') },
          { text: copy.configuration, link: pathFor(lang, 'guide/configuration') },
          { text: copy.advanced, link: pathFor(lang, 'guide/advanced') },
          { text: copy.whitepaperDoc, link: pathFor(lang, 'whitepaper') },
          { text: copy.evolution, link: pathFor(lang, 'evolution') },
        ],
      },
    ],
    [pathFor(lang, 'guide/')]: [
      {
        text: copy.overview,
        collapsed: false,
        items: [
          { text: copy.installation, link: pathFor(lang, 'guide/installation') },
          { text: copy.configuration, link: pathFor(lang, 'guide/configuration') },
          { text: copy.advanced, link: pathFor(lang, 'guide/advanced') },
        ],
      },
    ],
    [pathFor(lang, 'architecture/')]: [
      {
        text: copy.architecture,
        collapsed: false,
        items: [
          { text: copy.pipeline, link: pathFor(lang, 'architecture/pipeline') },
          { text: copy.container, link: pathFor(lang, 'architecture/container') },
          { text: copy.protocols, link: pathFor(lang, 'architecture/protocols') },
        ],
      },
    ],
    [pathFor(lang, 'algorithms/')]: [
      {
        text: copy.algorithms,
        collapsed: false,
        items: [
          { text: copy.ruleEngine, link: pathFor(lang, 'algorithms/rule-engine') },
          { text: copy.mlClassifier, link: pathFor(lang, 'algorithms/ml-classifier') },
          { text: copy.semanticAnalyzer, link: pathFor(lang, 'algorithms/semantic-analyzer') },
          { text: copy.llmIntegration, link: pathFor(lang, 'algorithms/llm-integration') },
          { text: copy.fusion, link: pathFor(lang, 'algorithms/fusion') },
        ],
      },
    ],
    [pathFor(lang, 'performance/')]: [
      {
        text: copy.performance,
        collapsed: false,
        items: [
          { text: copy.concurrency, link: pathFor(lang, 'performance/concurrency') },
          { text: copy.caching, link: pathFor(lang, 'performance/caching') },
          { text: copy.optimization, link: pathFor(lang, 'performance/optimization') },
        ],
      },
    ],
    [pathFor(lang, 'whitepaper')]: [
      {
        text: copy.whitepaper,
        collapsed: false,
        items: [
          { text: copy.whitepaperDoc, link: pathFor(lang, 'whitepaper') },
          { text: copy.evolution, link: pathFor(lang, 'evolution') },
          { text: copy.adr, link: pathFor(lang, 'adr') },
        ],
      },
    ],
    [pathFor(lang, 'evolution')]: [
      {
        text: copy.whitepaper,
        collapsed: false,
        items: [
          { text: copy.whitepaperDoc, link: pathFor(lang, 'whitepaper') },
          { text: copy.evolution, link: pathFor(lang, 'evolution') },
          { text: copy.adr, link: pathFor(lang, 'adr') },
        ],
      },
    ],
    [pathFor(lang, 'adr')]: [
      {
        text: copy.whitepaper,
        collapsed: false,
        items: [
          { text: copy.whitepaperDoc, link: pathFor(lang, 'whitepaper') },
          { text: copy.evolution, link: pathFor(lang, 'evolution') },
          { text: copy.adr, link: pathFor(lang, 'adr') },
        ],
      },
    ],
    [pathFor(lang, 'resources/')]: [
      {
        text: copy.references,
        collapsed: false,
        items: [
          { text: copy.referencesDoc, link: pathFor(lang, 'resources/references') },
          { text: copy.relatedProjects, link: pathFor(lang, 'resources/related-projects') },
        ],
      },
    ],
    [pathFor(lang, 'reference/')]: [
      {
        text: copy.referenceDocs,
        collapsed: false,
        items: [
          { text: copy.cli, link: pathFor(lang, 'reference/cli') },
          { text: copy.config, link: pathFor(lang, 'reference/config') },
          { text: copy.taxonomy, link: pathFor(lang, 'reference/taxonomy') },
        ],
      },
    ],
    [pathFor(lang, 'engineering/')]: [
      {
        text: copy.engineering,
        collapsed: false,
        items: [
          { text: copy.testingStrategy, link: pathFor(lang, 'engineering/testing-strategy') },
          { text: copy.ciCd, link: pathFor(lang, 'engineering/ci-cd') },
        ],
      },
    ],
  }
}

export function resolvePreferredLocale(storedLocale, navigatorLanguage = '') {
  if (storedLocale === 'zh' || storedLocale === 'en') {
    return storedLocale
  }

  return navigatorLanguage.toLowerCase().startsWith('zh') ? 'zh' : 'en'
}

const resolvePreferredLocaleSource = resolvePreferredLocale.toString()

export const localeRedirectScript = `
  (function() {
    const key = 'bookmarks-cleaner-lang';
    const base = document.querySelector('base')?.getAttribute('href') || '/';
    const path = location.pathname;
    const isRoot = path === base || path === base + 'index.html' || path === '/' || path === '/index.html';
    if (!isRoot) return;

    const stored = localStorage.getItem(key);
    const resolvePreferredLocale = ${resolvePreferredLocaleSource};
    const targetLang = resolvePreferredLocale(stored, navigator.language || '');

    if (!stored) {
      localStorage.setItem(key, targetLang);
    }

    location.replace(base + targetLang + '/');
  })();
`.trim()

export function createLocaleThemeConfig(lang) {
  const copy = localeText[lang]

  return {
    nav: themeNav(lang),
    sidebar: themeSidebar(lang),
    editLink: {
      pattern: `${REPO}/edit/master/docs/:path`,
      text: copy.editLink,
    },
    outline: { level: [2, 3], label: copy.outline },
    docFooter: { prev: copy.prev, next: copy.next },
    lastUpdated: { text: copy.lastUpdated },
    returnToTopLabel: copy.returnToTop,
    sidebarMenuLabel: copy.sidebarMenu,
    darkModeSwitchLabel: copy.darkModeSwitch,
    footer: {
      message: footerMessage,
      copyright: `Copyright © 2025-${new Date().getFullYear()} LessUp`,
    },
  }
}
