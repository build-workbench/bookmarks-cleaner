import DefaultTheme from 'vitepress/theme'
import { onMounted } from 'vue'
import './style.css'

const STORAGE_KEY = 'bookmarks-cleaner-lang'

function getBasePath(): string {
  // VitePress 在运行时提供 __VP_SITE_DATA__ 包含 base 路径
  const siteData = (window as any).__VP_SITE_DATA__
  return siteData?.base || '/'
}

function shouldRedirect(): boolean {
  const pathname = window.location.pathname
  const base = getBasePath()

  // 规范化路径：移除尾随斜杠进行比较
  const normalizedPath = pathname.replace(/\/$/, '') || '/'
  const normalizedBase = base.replace(/\/$/, '') || '/'

  // 只在根路径（考虑 base）执行自动跳转
  // 例如：base="/bookmarks-cleaner/" 时，路径应为 "/bookmarks-cleaner" 或 "/bookmarks-cleaner/index.html"
  const isRoot = normalizedPath === normalizedBase ||
                 normalizedPath === normalizedBase + '/index.html' ||
                 pathname === '/' ||
                 pathname === '/index.html'

  return isRoot
}

function redirectToLanguage() {
  // 检查是否应该执行重定向
  if (!shouldRedirect()) {
    return
  }

  const base = getBasePath()

  // 优先使用存储的语言偏好
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    const target = `${base}${stored}/`
    window.location.replace(target)
    return
  }

  // 首次访问：根据浏览器语言跳转并存储偏好
  const browserLang = navigator.language || (navigator as any).userLanguage || ''
  const targetLang = browserLang.toLowerCase().startsWith('zh') ? 'zh' : 'en'
  localStorage.setItem(STORAGE_KEY, targetLang)
  window.location.replace(`${base}${targetLang}/`)
}

export default {
  ...DefaultTheme,
  setup() {
    onMounted(() => {
      // 延迟执行以确保 VitePress 初始化完成
      // 使用 requestAnimationFrame 确保在下一帧执行，避免与 VitePress 路由冲突
      requestAnimationFrame(() => {
        redirectToLanguage()
      })
    })
  }
}
