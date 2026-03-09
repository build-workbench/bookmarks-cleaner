import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "zh-CN",
  title: "CleanBook",
  description: "智能书签清理与分类：规则 + ML + LLM（可选）",

  // GitHub Pages 部署时的 base 路径
  base: "/bookmarks-cleaner/",

  lastUpdated: true,
  cleanUrls: true,

  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: "/bookmarks-cleaner/favicon.svg" }],
  ],

  themeConfig: {
    logo: "/favicon.svg",

    nav: [
      { text: "快速上手", link: "/quickstart_zh" },
      { text: "设计文档", link: "/DESIGN" },
      {
        text: "深入",
        items: [
          { text: "系统架构", link: "/design/system_architecture" },
          { text: "ML 设计", link: "/design/ml_design_zh" },
          { text: "LLM 提示词", link: "/llm_prompt_templates" },
          { text: "技术报告", link: "/technical_report" },
        ],
      },
      {
        text: "GitHub",
        link: "https://github.com/LessUp/bookmarks-cleaner",
      },
    ],

    sidebar: [
      {
        text: "入门",
        items: [
          { text: "简介", link: "/" },
          { text: "快速上手", link: "/quickstart_zh" },
        ],
      },
      {
        text: "设计",
        items: [
          { text: "设计说明", link: "/DESIGN" },
          { text: "系统架构", link: "/design/system_architecture" },
          { text: "ML 设计", link: "/design/ml_design_zh" },
          { text: "书签管理最佳实践", link: "/design/bookmark_best_practices_zh" },
        ],
      },
      {
        text: "进阶",
        items: [
          { text: "LLM 提示词模板", link: "/llm_prompt_templates" },
          { text: "技术报告", link: "/technical_report" },
          { text: "开发指南", link: "/guides/development_guide" },
        ],
      },
    ],

    socialLinks: [
      { icon: "github", link: "https://github.com/LessUp/bookmarks-cleaner" },
    ],

    footer: {
      message: "MIT License",
      copyright: "© 2024-present LessUp",
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
