import { defineConfig } from "vitepress";

const SITE = {
  title: "CleanBook",
  description:
    "开发者的离线优先书签清理与分类工具：规则优先，ML 辅助，LLM 可选。",
  descriptionEn:
    "Offline-first bookmark cleaner for developers: rules-first, ML-assisted, LLM-optional.",
  repo: "https://github.com/LessUp/bookmarks-cleaner",
};

function meta(lang: "zh" | "en") {
  const isZh = lang === "zh";
  return [
    ["meta", { name: "description", content: isZh ? SITE.description : SITE.descriptionEn }],
    [
      "meta",
      {
        name: "keywords",
        content: isZh
          ? "书签清理,书签分类,离线工具,Python CLI,规则引擎,机器学习"
          : "bookmark cleaner,bookmark classification,offline tool,Python CLI,rules engine,machine learning",
      },
    ],
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:title", content: SITE.title }],
    ["meta", { property: "og:description", content: isZh ? SITE.description : SITE.descriptionEn }],
    ["link", { rel: "icon", type: "image/svg+xml", href: "/logo.svg" }],
    ["link", { rel: "manifest", href: "/manifest.json" }],
  ];
}

const zhNav = [
  { text: "快速开始", link: "/zh/quickstart" },
  { text: "安装", link: "/zh/guide/installation" },
  { text: "配置", link: "/zh/reference/config" },
  { text: "GitHub", link: SITE.repo },
];

const enNav = [
  { text: "Quick Start", link: "/en/quickstart" },
  { text: "Installation", link: "/en/guide/installation" },
  { text: "Configuration", link: "/en/reference/config" },
  { text: "GitHub", link: SITE.repo },
];

const zhSidebar = {
  "/zh/guide/": [
    {
      text: "使用指南",
      items: [
        { text: "安装", link: "/zh/guide/installation" },
        { text: "配置", link: "/zh/guide/configuration" },
      ],
    },
  ],
  "/zh/reference/": [
    {
      text: "参考",
      items: [
        { text: "配置项", link: "/zh/reference/config" },
        { text: "词表格式", link: "/zh/reference/taxonomy" },
      ],
    },
  ],
};

const enSidebar = {
  "/en/guide/": [
    {
      text: "Guide",
      items: [
        { text: "Installation", link: "/en/guide/installation" },
        { text: "Configuration", link: "/en/guide/configuration" },
      ],
    },
  ],
  "/en/reference/": [
    {
      text: "Reference",
      items: [
        { text: "Configuration", link: "/en/reference/config" },
        { text: "Taxonomy", link: "/en/reference/taxonomy" },
      ],
    },
  ],
};

export default defineConfig({
  base: "/bookmarks-cleaner/",
  lang: "zh-CN",
  title: SITE.title,
  description: SITE.description,
  cleanUrls: true,
  lastUpdated: true,
  head: meta("zh"),
  locales: {
    root: {
      label: "简体中文",
      lang: "zh-CN",
      title: SITE.title,
      description: SITE.description,
      head: meta("zh"),
      themeConfig: {
        nav: zhNav,
        sidebar: zhSidebar,
        editLink: {
          pattern: `${SITE.repo}/edit/master/docs/:path`,
          text: "在 GitHub 上编辑此页",
        },
        outline: { level: [2, 3], label: "本页内容" },
        docFooter: { prev: "上一页", next: "下一页" },
        lastUpdated: { text: "最后更新" },
        returnToTopLabel: "返回顶部",
        sidebarMenuLabel: "菜单",
        darkModeSwitchLabel: "切换主题",
        footer: {
          message: "CleanBook · Offline-first bookmark cleanup",
          copyright: `Copyright © 2025-${new Date().getFullYear()} LessUp`,
        },
      },
    },
    en: {
      label: "English",
      lang: "en-US",
      title: SITE.title,
      description: SITE.descriptionEn,
      head: meta("en"),
      themeConfig: {
        nav: enNav,
        sidebar: enSidebar,
        editLink: {
          pattern: `${SITE.repo}/edit/master/docs/:path`,
          text: "Edit this page on GitHub",
        },
        outline: { level: [2, 3], label: "On this page" },
        docFooter: { prev: "Previous", next: "Next" },
        lastUpdated: { text: "Last updated" },
        returnToTopLabel: "Return to top",
        sidebarMenuLabel: "Menu",
        darkModeSwitchLabel: "Appearance",
        footer: {
          message: "CleanBook · Offline-first bookmark cleanup",
          copyright: `Copyright © 2025-${new Date().getFullYear()} LessUp`,
        },
      },
    },
  },
  themeConfig: {
    logo: { src: "/logo.svg", alt: "CleanBook" },
    siteTitle: SITE.title,
    socialLinks: [{ icon: "github", link: SITE.repo }],
    search: { provider: "local" },
  },
  markdown: {
    lineNumbers: true,
  },
});
