export function createMermaidConfig() {
  return {
    theme: 'base',
    themeVariables: {
      background: 'transparent',
      primaryColor: 'var(--cb-bg-elevated)',
      primaryTextColor: 'var(--cb-text)',
      primaryBorderColor: 'var(--cb-border-strong)',
      secondaryColor: 'var(--cb-bg-soft)',
      secondaryTextColor: 'var(--cb-text)',
      secondaryBorderColor: 'var(--cb-border-strong)',
      tertiaryColor: 'color-mix(in srgb, var(--cb-accent) 10%, var(--cb-bg-elevated))',
      tertiaryTextColor: 'var(--cb-text)',
      tertiaryBorderColor: 'color-mix(in srgb, var(--cb-accent) 32%, var(--cb-border-strong))',
      lineColor: 'var(--cb-accent)',
      textColor: 'var(--cb-text)',
      mainBkg: 'var(--cb-bg-elevated)',
      nodeBkg: 'var(--cb-bg-elevated)',
      nodeBorder: 'var(--cb-border-strong)',
      clusterBkg: 'color-mix(in srgb, var(--cb-bg-soft) 76%, var(--cb-bg))',
      clusterBorder: 'var(--cb-border-strong)',
      edgeLabelBackground: 'var(--cb-bg-elevated)',
      fontFamily: 'var(--cb-font)',
    },
    flowchart: {
      curve: 'basis',
      padding: 20,
    },
  }
}
