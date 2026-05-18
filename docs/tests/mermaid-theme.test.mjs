import test from 'node:test'
import assert from 'node:assert/strict'

import { createMermaidConfig } from '../.vitepress/shared/mermaid-theme.mjs'

test('mermaid config uses the base theme with hardcoded color values (Mermaid does not support CSS variables)', () => {
  const config = createMermaidConfig()

  assert.equal(config.theme, 'base')
  assert.equal(config.flowchart.curve, 'basis')
  assert.equal(config.themeVariables.primaryColor, '#eef2ff')
  assert.equal(config.themeVariables.primaryTextColor, '#1a1e2e')
  assert.equal(config.themeVariables.lineColor, '#4477cc')
})
