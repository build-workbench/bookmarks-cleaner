import DefaultTheme from 'vitepress/theme'
import { h, onMounted } from 'vue'
import type { Theme } from 'vitepress'

// Import custom components
import HeroTerminal from './components/HeroTerminal.vue'
import DarkModeImage from './components/DarkModeImage.vue'
import FeatureCard from './components/FeatureCard.vue'
import ArchitectureFlow from './components/ArchitectureFlow.vue'
import CiteReference from './components/CiteReference.vue'

// Import styles
import './style.css'

const STORAGE_KEY = 'bookmarks-cleaner-lang'

function getBasePath(): string {
  const siteData = (window as any).__VP_SITE_DATA__
  return siteData?.base || '/'
}

function shouldRedirect(): boolean {
  const pathname = window.location.pathname
  const base = getBasePath()

  const normalizedPath = pathname.replace(/\/$/, '') || '/'
  const normalizedBase = base.replace(/\/$/, '') || '/'

  const isRoot = normalizedPath === normalizedBase ||
                 normalizedPath === normalizedBase + '/index.html' ||
                 pathname === '/' ||
                 pathname === '/index.html'

  return isRoot
}

function redirectToLanguage() {
  if (!shouldRedirect()) {
    return
  }

  const base = getBasePath()

  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    const target = `${base}${stored}/`
    window.location.replace(target)
    return
  }

  const browserLang = navigator.language || (navigator as any).userLanguage || ''
  const targetLang = browserLang.toLowerCase().startsWith('zh') ? 'zh' : 'en'
  localStorage.setItem(STORAGE_KEY, targetLang)
  window.location.replace(`${base}${targetLang}/`)
}

const theme: Theme = {
  extends: DefaultTheme,

  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      // Add HeroTerminal after home hero
      'home-hero-after': () => h(HeroTerminal),
    })
  },

  enhanceApp({ app }) {
    // Register global components
    app.component('HeroTerminal', HeroTerminal)
    app.component('DarkModeImage', DarkModeImage)
    app.component('FeatureCard', FeatureCard)
    app.component('ArchitectureFlow', ArchitectureFlow)
    app.component('CiteReference', CiteReference)
  },

  setup() {
    onMounted(() => {
      requestAnimationFrame(() => {
        redirectToLanguage()
      })
    })
  }
}

export default theme
