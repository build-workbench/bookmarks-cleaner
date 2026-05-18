/**
 * Mermaid theme configuration for CleanBook docs.
 *
 * NOTE: Mermaid's themeVariables do NOT support CSS custom properties
 * (var(--xxx)) — the Mermaid renderer processes these values in JavaScript
 * before mounting into the DOM, so CSS variable references are passed through
 * as literal strings and produce invisible or broken diagrams.
 *
 * We therefore hard-code two complete color palettes here and switch between
 * them at runtime via the `getMermaidConfig(isDark)` helper.
 */

const LIGHT = {
  // Backgrounds
  background: '#ffffff',
  mainBkg: '#fafbfd',
  nodeBkg: '#fafbfd',
  clusterBkg: '#f2f4fb',

  // Text
  primaryTextColor: '#1a1e2e',
  secondaryTextColor: '#3a4260',
  tertiaryTextColor: '#5a6480',
  textColor: '#1a1e2e',
  labelTextColor: '#1a1e2e',

  // Borders
  primaryBorderColor: '#c2c8da',
  secondaryBorderColor: '#d0d5e8',
  tertiaryBorderColor: '#c4ccdc',
  nodeBorder: '#c2c8da',
  clusterBorder: '#c8cedf',

  // Accent
  primaryColor: '#eef2ff',
  secondaryColor: '#f0f8f6',
  tertiaryColor: '#eef8f7',

  // Lines
  lineColor: '#4477cc',
  edgeLabelBackground: '#ffffff',

  // Specific tokens
  titleColor: '#1a1e2e',
  actorBkg: '#eef2ff',
  actorBorder: '#2055cc',
  actorTextColor: '#1a1e2e',
  activationBkgColor: '#f0f4ff',
  activationBorderColor: '#2055cc',
  noteBkgColor: '#fffbe8',
  noteBorderColor: '#d4a800',
  noteTextColor: '#5a4a00',
  labelBoxBkgColor: '#eef2ff',
  labelBoxBorderColor: '#c2c8da',

  // Loop / alt
  loopTextColor: '#3a4260',
  signalColor: '#2055cc',
  signalTextColor: '#1a1e2e',

  // Git graph
  git0: '#2055cc',
  git1: '#0e8c84',
  git2: '#b87000',
  git3: '#8040c0',
  git4: '#cc2050',
  gitBranchLabel0: '#ffffff',
  gitBranchLabel1: '#ffffff',
  gitBranchLabel2: '#ffffff',
  gitBranchLabel3: '#ffffff',
  gitBranchLabel4: '#ffffff',
}

const DARK = {
  // Backgrounds
  background: '#1a1e28',
  mainBkg: '#222736',
  nodeBkg: '#222736',
  clusterBkg: '#1e2234',

  // Text
  primaryTextColor: '#eef0f5',
  secondaryTextColor: '#b0b8cc',
  tertiaryTextColor: '#8b93a8',
  textColor: '#eef0f5',
  labelTextColor: '#eef0f5',

  // Borders
  primaryBorderColor: '#4a556e',
  secondaryBorderColor: '#3e4a60',
  tertiaryBorderColor: '#3a4558',
  nodeBorder: '#4a556e',
  clusterBorder: '#3e4a60',

  // Accent
  primaryColor: 'rgba(126,179,255,0.14)',
  secondaryColor: 'rgba(94,207,202,0.12)',
  tertiaryColor: 'rgba(240,192,96,0.12)',

  // Lines
  lineColor: '#5a8ccc',
  edgeLabelBackground: '#222736',

  // Specific tokens
  titleColor: '#eef0f5',
  actorBkg: 'rgba(126,179,255,0.14)',
  actorBorder: '#7eb3ff',
  actorTextColor: '#eef0f5',
  activationBkgColor: 'rgba(126,179,255,0.18)',
  activationBorderColor: '#7eb3ff',
  noteBkgColor: 'rgba(240,192,96,0.14)',
  noteBorderColor: '#f0c060',
  noteTextColor: '#f5e0a0',
  labelBoxBkgColor: 'rgba(126,179,255,0.12)',
  labelBoxBorderColor: '#4a556e',

  // Loop / alt
  loopTextColor: '#b0b8cc',
  signalColor: '#7eb3ff',
  signalTextColor: '#eef0f5',

  // Git graph
  git0: '#7eb3ff',
  git1: '#5ecfca',
  git2: '#f0c060',
  git3: '#c080ff',
  git4: '#ff7090',
  gitBranchLabel0: '#0e1420',
  gitBranchLabel1: '#0e1420',
  gitBranchLabel2: '#0e1420',
  gitBranchLabel3: '#0e1420',
  gitBranchLabel4: '#0e1420',
}

/**
 * Return a complete Mermaid config object.
 * Pass `isDark = true` for dark-mode diagrams.
 */
export function getMermaidConfig(isDark = false) {
  const vars = isDark ? DARK : LIGHT

  return {
    theme: 'base',
    themeVariables: vars,
    flowchart: {
      curve: 'basis',
      padding: 22,
      useMaxWidth: true,
    },
    sequence: {
      diagramMarginX: 50,
      diagramMarginY: 20,
      actorMargin: 80,
      boxTextMargin: 10,
      noteMargin: 10,
      messageMargin: 40,
      mirrorActors: false,
      useMaxWidth: true,
    },
  }
}

/**
 * Legacy export — returns a static light-mode config.
 * Kept for build-time config.ts compatibility.
 */
export function createMermaidConfig() {
  return getMermaidConfig(false)
}
