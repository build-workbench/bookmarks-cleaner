<script setup lang="ts">
import { computed } from 'vue'
import { getLandingContent } from '../home-content.mjs'

const content = computed(() => getLandingContent())
</script>

<template>
  <section class="cb-research-hero">
    <!-- Animated grid background -->
    <div class="cb-rh-grid" aria-hidden="true">
      <div class="cb-rh-grid-inner" />
    </div>

    <div class="cb-rh-body">
      <p class="cb-rh-kicker">
        <span class="cb-rh-kicker-dot" />
        {{ content.eyebrow }}
      </p>
      <div class="cb-rh-grid-content">
        <p class="cb-rh-abstract">{{ content.abstract }}</p>
        <ul class="cb-rh-theses">
          <li v-for="(item, idx) in content.theses" :key="item">
            <span class="cb-rh-thesis-num">{{ String(idx + 1).padStart(2, '0') }}</span>
            <span>{{ item }}</span>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cb-research-hero {
  position: relative;
  margin: 0 0 2rem;
  padding: 2rem 0 1.5rem;
  border-bottom: 1px solid var(--cb-border);
  overflow: hidden;
}

/* ── Animated grid background ── */
.cb-rh-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.cb-rh-grid-inner {
  position: absolute;
  inset: -50%;
  background-image:
    linear-gradient(var(--cb-border) 1px, transparent 1px),
    linear-gradient(90deg, var(--cb-border) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.5;
  animation: cb-grid-drift 24s linear infinite;
  mask-image: radial-gradient(ellipse 80% 90% at 50% 0%, black 10%, transparent 75%);
  -webkit-mask-image: radial-gradient(ellipse 80% 90% at 50% 0%, black 10%, transparent 75%);
}

@keyframes cb-grid-drift {
  from { transform: translate(0, 0); }
  to   { transform: translate(40px, 40px); }
}

/* ── Content ── */
.cb-rh-body {
  position: relative;
  z-index: 1;
}

.cb-rh-kicker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem;
  color: var(--cb-accent);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-family: var(--cb-font-mono);
}

.cb-rh-kicker-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--cb-accent);
  box-shadow: 0 0 8px var(--cb-accent);
  animation: cb-pulse 2s ease-in-out infinite;
  flex-shrink: 0;
}

@keyframes cb-pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--cb-accent); }
  50%       { opacity: 0.6; box-shadow: 0 0 16px var(--cb-accent); }
}

.cb-rh-grid-content {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr);
  gap: 1.25rem 2.5rem;
  align-items: start;
}

.cb-rh-abstract {
  margin: 0;
  color: var(--cb-text);
  font-size: clamp(1.05rem, 2.2vw, 1.3rem);
  line-height: 1.78;
  font-weight: 500;
  max-width: 42ch;
}

.cb-rh-theses {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.65rem;
}

.cb-rh-theses li {
  display: flex;
  gap: 0.75rem;
  align-items: baseline;
  padding: 0.9rem 1.05rem;
  border: 1px solid var(--cb-border);
  border-radius: var(--cb-radius-md);
  background: var(--cb-bg-elevated);
  color: var(--cb-text-2);
  font-size: 0.91rem;
  line-height: 1.65;
  transition: border-color var(--cb-motion-fast), background var(--cb-motion-fast);
}

.cb-rh-theses li:hover {
  border-color: var(--cb-border-accent);
  background: color-mix(in srgb, var(--cb-accent) 4%, var(--cb-bg-elevated));
}

.cb-rh-thesis-num {
  color: var(--cb-accent);
  font-family: var(--cb-font-mono);
  font-weight: 800;
  font-size: 0.75rem;
  flex-shrink: 0;
  margin-top: 0.05em;
  opacity: 0.7;
}

@media (max-width: 800px) {
  .cb-rh-grid-content {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .cb-rh-grid-inner {
    animation: none;
  }

  .cb-rh-kicker-dot {
    animation: none;
  }
}
</style>
