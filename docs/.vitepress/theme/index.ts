import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import type { Theme } from 'vitepress'

// Import custom components
import HeroTerminal from './components/HeroTerminal.vue'
import DarkModeImage from './components/DarkModeImage.vue'
import FeatureCard from './components/FeatureCard.vue'
import ArchitectureFlow from './components/ArchitectureFlow.vue'
import CiteReference from './components/CiteReference.vue'
import PipelineVisualizer from './components/PipelineVisualizer.vue'

// Import styles
import './style.css'

const theme: Theme = {
  extends: DefaultTheme,

  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      'home-hero-after': () => h(HeroTerminal),
    })
  },

  enhanceApp({ app }) {
    app.component('HeroTerminal', HeroTerminal)
    app.component('DarkModeImage', DarkModeImage)
    app.component('FeatureCard', FeatureCard)
    app.component('ArchitectureFlow', ArchitectureFlow)
    app.component('CiteReference', CiteReference)
    app.component('PipelineVisualizer', PipelineVisualizer)
  },
}

export default theme
