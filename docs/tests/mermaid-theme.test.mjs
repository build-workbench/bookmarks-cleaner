import test from 'node:test'
import assert from 'node:assert/strict'

import { createMermaidConfig } from '../.vitepress/shared/mermaid-theme.mjs'

test('mermaid config uses the base theme with CSS-variable driven tokens', () => {
  const config = createMermaidConfig()

  assert.equal(config.theme, 'base')
  assert.equal(config.flowchart.curve, 'basis')
  assert.equal(config.themeVariables.primaryColor, 'var(--cb-bg-elevated)')
  assert.equal(config.themeVariables.primaryTextColor, 'var(--cb-text)')
  assert.equal(config.themeVariables.lineColor, 'var(--cb-accent)')
})
