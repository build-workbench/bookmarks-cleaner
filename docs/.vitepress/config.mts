import { defineConfig } from "vitepress";

// 中文配置
const zhConfig = {
  lang: "zh-CN",
  title: "CleanBook",
  description: "智能书签清理与分类：规则优先，ML 辅助，LLM 可选",
  themeConfig: {
    nav: [
      { text: "首页", link: "/zh/" },
      { text: "快速开始", link: "/zh/quickstart" },
      { text: "使用指南", link: "/zh/guide/best-practices" },
      {
        text: "架构设计",
        items: [
          { text: "设计概述", link: "/zh/design/overview" },
          { text: "系统架构", link: "/zh/design/architecture" },
          { text: "ML 设计", link: "/zh/design/ml-design" },
        ],
      },
      { text: "开发指南", link: "/zh/guide/development" },
      { text: "参考", link: "/zh/reference/llm-templates" },
    ],
    sidebar: {
      "/zh/": [
        { text: "首页", link: "/zh/" },
        {
          text: "快速开始",
          items: [{ text: "快速上手", link: "/zh/quickstart" }],
        },
        {
          text: "使用指南",
          items: [
            { text: "书签管理最佳实践", link: "/zh/guide/best-practices" },
            { text: "开发指南", link: "/zh/guide/development" },
          ],
        },
        {
          text: "架构设计",
          items: [
            { text: "设计概述", link: "/zh/design/overview" },
            { text: "系统架构", link: "/zh/design/architecture" },
            { text: "ML 设计", link: "/zh/design/ml-design" },
          ],
        },
        {
          text: "参考",
          items: [{ text: "LLM 提示词模板", link: "/zh/reference/llm-templates" }],
        },
        {
          text: "高级",
          items: [{ text: "技术报告", link: "/zh/advanced/technical-report" }],
        },
      ],
    },
  },
};

// English configuration
const enConfig = {
  lang: "en-US",
  title: "CleanBook",
  description: "Smart bookmark cleaning and classification: Rules-first, ML-assisted, LLM-optional",
  themeConfig: {
    nav: [
      { text: "Home", link: "/en/" },
      { text: "Quick Start", link: "/en/quickstart" },
      { text: "Guide", link: "/en/guide/best-practices" },
      {
        text: "Design",
        items: [
          { text: "Overview", link: "/en/design/overview" },
          { text: "Architecture", link: "/en/design/architecture" },
          { text: "ML Design", link: "/en/design/ml-design" },
        ],
      },
      { text: "Development", link: "/en/guide/development" },
      { text: "Reference", link: "/en/reference/llm-templates" },
    ],
    sidebar: {
      "/en/": [
        { text: "Home", link: "/en/" },
        {
          text: "Quick Start",
          items: [{ text: "Quick Start", link: "/en/quickstart" }],
        },
        {
          text: "Guide",
          items: [
            { text: "Best Practices", link: "/en/guide/best-practices" },
            { text: "Development", link: "/en/guide/development" },
          ],
        },
        {
          text: "Design",
          items: [
            { text: "Overview", link: "/en/design/overview" },
            { text: "Architecture", link: "/en/design/architecture" },
            { text: "ML Design", link: "/en/design/ml-design" },
          ],
        },
        {
          text: "Reference",
          items: [{ text: "LLM Templates", link: "/en/reference/llm-templates" }],
        },
        {
          text: "Advanced",
          items: [{ text: "Technical Report", link: "/en/advanced/technical-report" }],
        },
      ],
    },
  },
};

// Determine current language from URL
const getLang = (pathname: string) => {
  if (pathname.startsWith("/en")) return "en";
  return "zh";
};

export default defineConfig({
  base: "/bookmarks-cleaner/",
  lastUpdated: true,
  cleanUrls: true,

  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: "/logo.svg" }],
    ["link", { rel: "canonical", href: "https://lessup.github.io/bookmarks-cleaner/" }],
    ["meta", { name: "theme-color", content: "#0f172a" }],
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:title", content: "CleanBook" }],
    ["meta", { property: "og:description", content: "Smart bookmark cleaning and classification" }],
    ["meta", { property: "og:url", content: "https://lessup.github.io/bookmarks-cleaner/" }],
  ],

  locales: {
    root: {
      label: "中文",
      lang: "zh-CN",
      ...zhConfig,
    },
    en: {
      label: "English",
      lang: "en-US",
      ...enConfig,
    },
  },

  themeConfig: {
    logo: "/logo.svg",

    socialLinks: [
      { icon: "github", link: "https://github.com/LessUp/bookmarks-cleaner" },
    ],

    footer: {
      message: "Released under MIT License",
      copyright: "Copyright © 2025-2026 LessUp",
    },

    editLink: {
      pattern: "https://github.com/LessUp/bookmarks-cleaner/edit/master/docs/:path",
      text: "Edit this page on GitHub",
    },

    outline: {
      level: [2, 3],
      label: "On this page",
    },

    docFooter: {
      prev: "Previous",
      next: "Next",
    },

    lastUpdated: {
      text: "Last updated",
    },

    returnToTopLabel: "Return to top",
    sidebarMenuLabel: "Menu",
    darkModeSwitchLabel: "Theme",
    externalLinkIcon: true,

    search: {
      provider: "local",
      options: {
        translations: {
          button: { buttonText: "Search docs", buttonAriaLabel: "Search documentation" },
          modal: {
            noResultsText: "No results found",
            resetButtonTitle: "Clear query",
            footer: { selectText: "Select", navigateText: "Navigate", closeText: "Close" },
          },
        },
      },
    },
  },
});
