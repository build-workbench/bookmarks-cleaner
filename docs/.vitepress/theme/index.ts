import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import './styles/custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    // Register global components if needed
  },
} satisfies Theme
