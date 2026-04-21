import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import { h, onMounted } from 'vue'
import './styles/main.css'
import './styles/custom.css'
import './styles/animations.css'
import './styles/components.css'

// Import custom components
import FeatureCard from './components/FeatureCard.vue'
import TerminalDemo from './components/TerminalDemo.vue'
import ConfigGenerator from './components/ConfigGenerator.vue'
import PipelineDiagram from './components/PipelineDiagram.vue'
import StatsCounter from './components/StatsCounter.vue'
import CodeGroup from './components/CodeGroup.vue'
import HomeHero from './components/HomeHero.vue'
import ProjectStructure from './components/ProjectStructure.vue'

// Register Service Worker for PWA
const registerSW = () => {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/bookmarks-cleaner/sw.js')
        .then((registration) => {
          console.log('[SW] Registered:', registration.scope)

          // Check for updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  // New content available
                  console.log('[SW] New content available, please refresh')
                }
              })
            }
          })
        })
        .catch((error) => {
          console.log('[SW] Registration failed:', error)
        })
    })
  }
}

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      // Layout slots can be customized here
    })
  },
  enhanceApp({ app, router, siteData }) {
    // Register custom components
    app.component('FeatureCard', FeatureCard)
    app.component('TerminalDemo', TerminalDemo)
    app.component('ConfigGenerator', ConfigGenerator)
    app.component('PipelineDiagram', PipelineDiagram)
    app.component('StatsCounter', StatsCounter)
    app.component('CodeGroup', CodeGroup)
    app.component('HomeHero', HomeHero)
    app.component('ProjectStructure', ProjectStructure)

    // Register service worker after app mount
    if (typeof window !== 'undefined') {
      registerSW()
    }
  },
} satisfies Theme
