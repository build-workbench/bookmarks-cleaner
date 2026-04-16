---
layout: home
---

<head>
  <meta http-equiv="refresh" content="0; url=/bookmarks-cleaner/zh/">
  <link rel="canonical" href="/bookmarks-cleaner/zh/">
</head>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vitepress'

const router = useRouter()

onMounted(() => {
  // Redirect to Chinese version as default
  router.go('/zh/')
})
</script>

<div style="text-align: center; padding: 4rem 2rem;">
  <h1>CleanBook</h1>
  <p>正在跳转...</p>
  <p>
    <a href="/bookmarks-cleaner/zh/">中文</a> |
    <a href="/bookmarks-cleaner/en/">English</a>
  </p>
</div>
