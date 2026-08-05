const REPO = 'https://github.com/LessUp/bookmarks-cleaner'

const footerMessage = 'Bookmarks Cleaner · 离线优先的书签清理'

const sidebar = {
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
}

function pathFor(suffix = '') {
  return suffix ? `/zh/${suffix}` : '/zh/'
}

function themeNav() {
  return [
    { text: '导读', link: pathFor() },
    { text: '架构', link: pathFor('architecture/pipeline') },
    { text: '算法', link: pathFor('algorithms/fusion') },
    { text: '性能', link: pathFor('performance/optimization') },
    { text: '白皮书', link: pathFor('whitepaper') },
    { text: '参考', link: pathFor('resources/references') },
    { text: 'GitHub', link: REPO },
  ]
}

function themeSidebar() {
  const base = '/zh/'
  const c = sidebar

  return {
    [base]: [
      {
        text: c.overview,
        collapsed: false,
        items: [
          { text: c.home, link: base },
          { text: c.installation, link: pathFor('guide/installation') },
          { text: c.configuration, link: pathFor('guide/configuration') },
          { text: c.advanced, link: pathFor('guide/advanced') },
          { text: c.whitepaperDoc, link: pathFor('whitepaper') },
          { text: c.evolution, link: pathFor('evolution') },
        ],
      },
    ],
    [pathFor('guide/')]: [
      {
        text: c.overview,
        collapsed: false,
        items: [
          { text: c.installation, link: pathFor('guide/installation') },
          { text: c.configuration, link: pathFor('guide/configuration') },
          { text: c.advanced, link: pathFor('guide/advanced') },
        ],
      },
    ],
    [pathFor('architecture/')]: [
      {
        text: c.architecture,
        collapsed: false,
        items: [
          { text: c.pipeline, link: pathFor('architecture/pipeline') },
          { text: c.container, link: pathFor('architecture/container') },
          { text: c.protocols, link: pathFor('architecture/protocols') },
        ],
      },
    ],
    [pathFor('algorithms/')]: [
      {
        text: c.algorithms,
        collapsed: false,
        items: [
          { text: c.ruleEngine, link: pathFor('algorithms/rule-engine') },
          { text: c.mlClassifier, link: pathFor('algorithms/ml-classifier') },
          { text: c.semanticAnalyzer, link: pathFor('algorithms/semantic-analyzer') },
          { text: c.llmIntegration, link: pathFor('algorithms/llm-integration') },
          { text: c.fusion, link: pathFor('algorithms/fusion') },
        ],
      },
    ],
    [pathFor('performance/')]: [
      {
        text: c.performance,
        collapsed: false,
        items: [
          { text: c.concurrency, link: pathFor('performance/concurrency') },
          { text: c.caching, link: pathFor('performance/caching') },
          { text: c.optimization, link: pathFor('performance/optimization') },
        ],
      },
    ],
    [pathFor('whitepaper')]: [
      {
        text: c.whitepaper,
        collapsed: false,
        items: [
          { text: c.whitepaperDoc, link: pathFor('whitepaper') },
          { text: c.evolution, link: pathFor('evolution') },
          { text: c.adr, link: pathFor('adr') },
        ],
      },
    ],
    [pathFor('evolution')]: [
      {
        text: c.whitepaper,
        collapsed: false,
        items: [
          { text: c.whitepaperDoc, link: pathFor('whitepaper') },
          { text: c.evolution, link: pathFor('evolution') },
          { text: c.adr, link: pathFor('adr') },
        ],
      },
    ],
    [pathFor('adr')]: [
      {
        text: c.whitepaper,
        collapsed: false,
        items: [
          { text: c.whitepaperDoc, link: pathFor('whitepaper') },
          { text: c.evolution, link: pathFor('evolution') },
          { text: c.adr, link: pathFor('adr') },
        ],
      },
    ],
    [pathFor('resources/')]: [
      {
        text: c.references,
        collapsed: false,
        items: [
          { text: c.referencesDoc, link: pathFor('resources/references') },
          { text: c.relatedProjects, link: pathFor('resources/related-projects') },
        ],
      },
    ],
    [pathFor('reference/')]: [
      {
        text: c.referenceDocs,
        collapsed: false,
        items: [
          { text: c.cli, link: pathFor('reference/cli') },
          { text: c.config, link: pathFor('reference/config') },
          { text: c.taxonomy, link: pathFor('reference/taxonomy') },
        ],
      },
    ],
    [pathFor('engineering/')]: [
      {
        text: c.engineering,
        collapsed: false,
        items: [
          { text: c.testingStrategy, link: pathFor('engineering/testing-strategy') },
          { text: c.ciCd, link: pathFor('engineering/ci-cd') },
        ],
      },
    ],
  }
}

export function createThemeConfig() {
  return {
    nav: themeNav(),
    sidebar: themeSidebar(),
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
      message: footerMessage,
      copyright: `Copyright © 2025-${new Date().getFullYear()} LessUp`,
    },
  }
}
