const landingContent = {
  eyebrow: '面向离线优先书签分类 CLI 的系统导读',
  abstract: 'Bookmarks Cleaner 在这里不是一个"功能列表"，而是一份系统工件：关注架构边界、分类器协作、性能权衡，以及规则优先融合栈背后的工程理由。',
  theses: [
    '规则优先保证高频场景保持确定性与可解释性。',
    '融合层把 ML、语义分析与可选 LLM 协作纳入同一决策框架，而不是强制依赖它们。',
    '整站按"先理解运行时模型，再阅读实现细节"的方式组织。',
  ],
  metrics: [
    { label: '处理速度', value: '420-650/s', note: 'Ryzen 5 5600X 上的书签吞吐' },
    { label: '冷启动', value: '<100 ms', note: '重型依赖按需延迟初始化' },
    { label: '运行模式', value: '规则 · ML · LLM', note: '智能层可选，CLI 入口一致' },
    { label: '输出形式', value: 'HTML · JSON · MD', note: '同时覆盖人工阅读与机器消费' },
  ],
  evidence: [
    { title: '融合架构', detail: '加权投票保留异构分类器的可解释性，避免再训练一个额外融合层。', href: '/zh/algorithms/fusion' },
    { title: '离线保证', detail: '主执行路径始终本地化，可选 LLM 能力是附加层，不是基础依赖。', href: '/zh/whitepaper' },
    { title: '可组合运行时', detail: 'Facade、Coordinator、Pipeline 与 Protocol 边界共同压缩改动爆炸半径。', href: '/zh/architecture/pipeline' },
    { title: '性能证据', detail: '性能页面明确并发、缓存与吞吐结论背后的测试假设。', href: '/zh/performance/optimization' },
  ],
  paths: [
    { index: '01', title: '先读白皮书', detail: '先建立系统命题、边界与失败模型，再进入代码级实现。', href: '/zh/whitepaper' },
    { index: '02', title: '沿架构追踪', detail: '从 CLI 入口一路跟到协调层、流水线、分类器和导出层。', href: '/zh/architecture/pipeline' },
    { index: '03', title: '深挖算法', detail: '把规则匹配、语义辅助和融合权重当作协作层，而不是混成一团的"AI 能力"。', href: '/zh/algorithms/fusion' },
    { index: '04', title: '检查性能证据', detail: '阅读并发策略、缓存设计和性能数字成立的边界条件。', href: '/zh/performance/optimization' },
    { index: '05', title: '工程实践', detail: '了解测试策略、CI/CD 配置和贡献流程。', href: '/zh/engineering/testing-strategy' },
  ],
  citations: [
    { title: 'Kuncheva 2004', detail: '为融合引擎提供分类器组合理论背景。', href: '/zh/resources/references' },
    { title: 'Zadrozny & Elkan 2001', detail: '为置信度校准提供方法论来源。', href: '/zh/resources/references' },
    { title: '相关项目研究', detail: '用部署模型与智能能力对照 linkding、Shaarli 等项目。', href: '/zh/resources/related-projects' },
    { title: '演进记录', detail: '追踪系统如何从上帝类重构为 facade + pipeline。', href: '/zh/evolution' },
  ],
}

export function getLandingContent() {
  return landingContent
}
