import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'

// Import custom components
import HeroTerminal from './components/HeroTerminal.vue'
import DarkModeImage from './components/DarkModeImage.vue'
import ThemedFigure from './components/ThemedFigure.vue'
import FeatureCard from './components/FeatureCard.vue'
import ArchitectureFlow from './components/ArchitectureFlow.vue'
import ResearchHero from './components/ResearchHero.vue'
import BenchmarkStrip from './components/BenchmarkStrip.vue'
import SystemMap from './components/SystemMap.vue'
import EvidenceGrid from './components/EvidenceGrid.vue'
import ReadingPathGrid from './components/ReadingPathGrid.vue'
import CitationCluster from './components/CitationCluster.vue'
import CiteReference from './components/CiteReference.vue'
import PipelineVisualizer from './components/PipelineVisualizer.vue'
import PerformanceChart from './components/PerformanceChart.vue'
import ArchitectureMatrix from './components/ArchitectureMatrix.vue'

// Import styles
import './style.css'

const theme: Theme = {
  extends: DefaultTheme,

  enhanceApp({ app }) {
    app.component('HeroTerminal', HeroTerminal)
    app.component('DarkModeImage', DarkModeImage)
    app.component('ThemedFigure', ThemedFigure)
    app.component('FeatureCard', FeatureCard)
    app.component('ArchitectureFlow', ArchitectureFlow)
    app.component('ResearchHero', ResearchHero)
    app.component('BenchmarkStrip', BenchmarkStrip)
    app.component('SystemMap', SystemMap)
    app.component('EvidenceGrid', EvidenceGrid)
    app.component('ReadingPathGrid', ReadingPathGrid)
    app.component('CitationCluster', CitationCluster)
    app.component('CiteReference', CiteReference)
    app.component('PipelineVisualizer', PipelineVisualizer)
    app.component('PerformanceChart', PerformanceChart)
    app.component('ArchitectureMatrix', ArchitectureMatrix)
  },
}

export default theme
