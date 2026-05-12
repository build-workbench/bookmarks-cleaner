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

const STORAGE_KEY = 'bookmarks-cleaner-lang'

onMounted(() => {
  // 只在根路径执行跳转
  const isRoot = window.location.pathname === '/' || 
                 window.location.pathname === '/index.html'
  if (!isRoot) return
  
  // 优先使用存储的语言偏好
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    const target = stored === 'zh' ? '/zh/' : '/en/'
    window.location.replace(target)
    return
  }
  
  // 首次访问：根据浏览器语言跳转并存储偏好
  const browserLang = navigator.language || navigator.userLanguage || ''
  const targetLang = browserLang.toLowerCase().startsWith('zh') ? 'zh' : 'en'
  localStorage.setItem(STORAGE_KEY, targetLang)
  window.location.replace(targetLang === 'zh' ? '/zh/' : '/en/')
})
</script>
