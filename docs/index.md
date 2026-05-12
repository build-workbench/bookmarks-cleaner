---
layout: home
hero:
  name: Bookmarks Cleaner
  text: ' '
  actions:
    - theme: brand
      text: 简体中文
      link: /zh/
    - theme: alt
      text: English
      link: /en/
---

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vitepress'

onMounted(() => {
  const lang = navigator.language || navigator.userLanguage
  const target = lang.startsWith('zh') ? '/zh/' : '/en/'
  useRouter().go(target)
})
</script>
