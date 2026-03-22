import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "zh-CN",
  title: "CleanBook",
  description: "智能书签清理与分类：默认离线可用，支持规则、ML 与可选 LLM",
  base: "/bookmarks-cleaner/",
  lastUpdated: true,
  cleanUrls: true,
  head: [
    ["link", { rel: "canonical", href: "https://lessup.github.io/bookmarks-cleaner/" }],
    ["meta", { name: "theme-color", content: "#0f172a" }],
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:title", content: "CleanBook" }],
    ["meta", { property: "og:description", content: "智能书签清理与分类：默认离线可用，支持规则、ML 与可选 LLM" }],
    ["meta", { property: "og:url", content: "https://lessup.github.io/bookmarks-cleaner/" }],
    ["meta", { name: "twitter:card", content: "summary" }],
    ["meta", { name: "twitter:title", content: "CleanBook" }],
    ["meta", { name: "twitter:description", content: "默认离线可用的书签清理与分类工具，支持规则、ML 与可选 LLM" }],
  ],

  themeConfig: {
    nav: [
      { text: "概览", link: "/" },
      { text: "快速开始", link: "/quickstart_zh" },
      { text: "使用指南", link: "/design/bookmark_best_practices_zh" },
      {
        text: "架构设计",
        items: [
          { text: "设计说明", link: "/DESIGN" },
          { text: "系统架构", link: "/design/system_architecture" },
          { text: "ML 设计", link: "/design/ml_design_zh" },
        ],
      },
      { text: "开发指南", link: "/guides/development_guide" },
      { text: "参考", link: "/llm_prompt_templates" },
      { text: "归档", link: "/technical_report" },
    ],

    sidebar: [
      {
        text: "概览",
        items: [{ text: "文档首页", link: "/" }],
      },
      {
        text: "快速开始",
        items: [{ text: "快速上手", link: "/quickstart_zh" }],
      },
      {
        text: "使用指南",
        items: [{ text: "书签管理最佳实践", link: "/design/bookmark_best_practices_zh" }],
      },
      {
        text: "架构设计",
        items: [
          { text: "设计说明", link: "/DESIGN" },
          { text: "系统架构", link: "/design/system_architecture" },
          { text: "ML 设计", link: "/design/ml_design_zh" },
        ],
      },
      {
        text: "开发指南",
        items: [{ text: "开发指南", link: "/guides/development_guide" }],
      },
      {
        text: "参考",
        items: [{ text: "LLM 提示词模板", link: "/llm_prompt_templates" }],
      },
      {
        text: "归档",
        items: [{ text: "技术报告", link: "/technical_report" }],
      },
    ],

    editLink: {
      pattern: "https://github.com/LessUp/bookmarks-cleaner/edit/master/docs/:path",
      text: "在 GitHub 上编辑此页",
    },

    socialLinks: [{ icon: "github", link: "https://github.com/LessUp/bookmarks-cleaner" }],

    footer: {
      message: "基于 MIT 许可发布",
      copyright: "Copyright © 2025-2026 LessUp",
    },

    outline: {
      level: [2, 3],
      label: "页面导航",
    },

    docFooter: {
      prev: "上一篇",
      next: "下一篇",
    },

    lastUpdated: {
      text: "最后更新",
    },

    returnToTopLabel: "返回顶部",
    sidebarMenuLabel: "菜单",
    darkModeSwitchLabel: "主题",
    externalLinkIcon: true,

    search: {
      provider: "local",
      options: {
        translations: {
          button: { buttonText: "搜索文档", buttonAriaLabel: "搜索文档" },
          modal: {
            noResultsText: "未找到相关结果",
            resetButtonTitle: "清除查询",
            footer: { selectText: "选择", navigateText: "切换", closeText: "关闭" },
          },
        },
      },
    },
  },
});
