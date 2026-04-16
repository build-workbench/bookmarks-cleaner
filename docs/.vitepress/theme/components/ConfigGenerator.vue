<template>
  <div class="config-generator">
    <div class="config-header">
      <div class="config-title">
        <span class="title-icon">⚙️</span>
        <span>{{ title }}</span>
      </div>
      <div class="config-actions">
        <button class="btn btn-reset" @click="resetConfig">重置</button>
        <button class="btn btn-copy" @click="copyConfig">
          {{ copied ? '已复制!' : '复制配置' }}
        </button>
      </div>
    </div>
    
    <div class="config-body">
      <div class="config-form">
        <div 
          v-for="section in configSections" 
          :key="section.id"
          class="config-section"
        >
          <h4 class="section-title" @click="toggleSection(section.id)">
            <span class="section-toggle">{{ expandedSections.includes(section.id) ? '▼' : '▶' }}</span>
            {{ section.title }}
          </h4>
          
          <div v-show="expandedSections.includes(section.id)" class="section-fields">
            <div 
              v-for="field in section.fields" 
              :key="field.key"
              class="form-field"
            >
              <label :for="field.key">
                {{ field.label }}
                <span v-if="field.required" class="required">*</span>
              </label>
              
              <!-- String input -->
              <input
                v-if="field.type === 'string'"
                :id="field.key"
                v-model="config[field.key]"
                type="text"
                :placeholder="field.placeholder"
              />
              
              <!-- Number input -->
              <input
                v-else-if="field.type === 'number'"
                :id="field.key"
                v-model.number="config[field.key]"
                type="number"
                :min="field.min"
                :max="field.max"
                :step="field.step || 1"
              />
              
              <!-- Range slider -->
              <div v-else-if="field.type === 'range'" class="range-field">
                <input
                  :id="field.key"
                  v-model.number="config[field.key]"
                  type="range"
                  :min="field.min"
                  :max="field.max"
                  :step="field.step || 0.1"
                />
                <span class="range-value">{{ config[field.key] }}</span>
              </div>
              
              <!-- Select -->
              <select
                v-else-if="field.type === 'select'"
                :id="field.key"
                v-model="config[field.key]"
              >
                <option 
                  v-for="option in field.options" 
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
              
              <!-- Boolean -->
              <label v-else-if="field.type === 'boolean'" class="toggle-label">
                <input
                  :id="field.key"
                  v-model="config[field.key]"
                  type="checkbox"
                  class="toggle"
                />
                <span class="toggle-slider"></span>
                <span class="toggle-text">{{ config[field.key] ? '启用' : '禁用' }}</span>
              </label>
              
              <!-- Multi-select as checkboxes -->
              <div v-else-if="field.type === 'multiselect'" class="checkbox-group">
                <label 
                  v-for="option in field.options" 
                  :key="option.value"
                  class="checkbox-label"
                >
                  <input
                    type="checkbox"
                    :value="option.value"
                    v-model="config[field.key]"
                  />
                  {{ option.label }}
                </label>
              </div>
              
              <p v-if="field.description" class="field-description">{{ field.description }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="config-preview">
        <div class="preview-header">
          <span class="preview-filename">config.json</span>
        </div>
        <pre class="preview-code"><code v-html="highlightedOutput"></code></pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface FieldOption {
  value: string | number | boolean
  label: string
}

interface ConfigField {
  key: string
  label: string
  type: 'string' | 'number' | 'range' | 'select' | 'boolean' | 'multiselect'
  required?: boolean
  placeholder?: string
  min?: number
  max?: number
  step?: number
  options?: FieldOption[]
  description?: string
  default?: any
}

interface ConfigSection {
  id: string
  title: string
  fields: ConfigField[]
}

interface Props {
  title?: string
  sections: ConfigSection[]
  defaultConfig?: Record<string, any>
}

const props = withDefaults(defineProps<Props>(), {
  title: '配置生成器',
  defaultConfig: () => ({})
})

const config = ref<Record<string, any>>({
  ...getDefaultValues(),
  ...props.defaultConfig
})

const expandedSections = ref<string[]>(props.sections.map(s => s.id))
const copied = ref(false)

function getDefaultValues(): Record<string, any> {
  const defaults: Record<string, any> = {}
  props.sections.forEach(section => {
    section.fields.forEach(field => {
      if (field.default !== undefined) {
        defaults[field.key] = field.default
      } else if (field.type === 'boolean') {
        defaults[field.key] = false
      } else if (field.type === 'multiselect') {
        defaults[field.key] = []
      } else if (field.type === 'number' || field.type === 'range') {
        defaults[field.key] = field.min || 0
      } else {
        defaults[field.key] = ''
      }
    })
  })
  return defaults
}

const configSections = computed(() => props.sections)

const output = computed(() => {
  const output: Record<string, any> = {}
  
  props.sections.forEach(section => {
    const sectionOutput: Record<string, any> = {}
    let hasValues = false
    
    section.fields.forEach(field => {
      const value = config.value[field.key]
      if (value !== undefined && value !== '' && 
          !(Array.isArray(value) && value.length === 0)) {
        sectionOutput[field.key] = value
        hasValues = true
      }
    })
    
    if (hasValues) {
      output[section.title.toLowerCase().replace(/\s+/g, '_')] = sectionOutput
    }
  })
  
  return JSON.stringify(output, null, 2)
})

const highlightedOutput = computed(() => {
  return output.value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/(".*?"):/g, '<span class="token-key">$1</span>:')
    .replace(/: (".*?")/g, ': <span class="token-string">$1</span>')
    .replace(/: (\d+\.?\d*)/g, ': <span class="token-number">$1</span>')
    .replace(/: (true|false)/g, ': <span class="token-boolean">$1</span>')
})

const toggleSection = (id: string) => {
  const index = expandedSections.value.indexOf(id)
  if (index > -1) {
    expandedSections.value.splice(index, 1)
  } else {
    expandedSections.value.push(id)
  }
}

const resetConfig = () => {
  config.value = getDefaultValues()
}

const copyConfig = async () => {
  try {
    await navigator.clipboard.writeText(output.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.config-generator {
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--cb-radius-lg);
  overflow: hidden;
  margin: 1.5rem 0;
  background: var(--vp-c-bg);
  box-shadow: var(--cb-shadow-md);
}

.config-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: var(--vp-c-bg-soft);
  border-bottom: 1px solid var(--vp-c-divider);
}

.config-title {
  font-weight: 600;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-icon {
  font-size: 1.25rem;
}

.config-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: var(--cb-radius);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-reset {
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-2);
}

.btn-reset:hover {
  background: var(--vp-c-bg-alt);
}

.btn-copy {
  background: var(--cb-brand);
  border: none;
  color: white;
}

.btn-copy:hover {
  background: var(--cb-brand-dark);
}

.config-body {
  display: grid;
  grid-template-columns: 320px 1fr;
  min-height: 400px;
}

.config-form {
  padding: 1rem;
  background: var(--vp-c-bg-alt);
  border-right: 1px solid var(--vp-c-divider);
  overflow-y: auto;
  max-height: 500px;
}

.config-section {
  margin-bottom: 1rem;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.625rem 0.75rem;
  background: var(--vp-c-bg);
  border-radius: var(--cb-radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  transition: all 0.2s ease;
}

.section-title:hover {
  background: var(--vp-c-bg-soft);
}

.section-toggle {
  font-size: 0.625rem;
  color: var(--vp-c-text-3);
}

.section-fields {
  padding: 0.75rem;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-field {
  margin-bottom: 1rem;
}

.form-field:last-child {
  margin-bottom: 0;
}

.form-field label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 0.375rem;
  color: var(--vp-c-text-1);
}

.required {
  color: var(--cb-accent-red);
}

.form-field input[type="text"],
.form-field input[type="number"],
.form-field select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--cb-radius);
  background: var(--vp-c-bg);
  font-size: 0.875rem;
  transition: all 0.2s ease;
  color: var(--vp-c-text-1);
}

.form-field input:focus,
.form-field select:focus {
  outline: none;
  border-color: var(--cb-brand);
  box-shadow: 0 0 0 2px var(--vp-c-brand-soft);
}

.range-field {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.range-field input[type="range"] {
  flex: 1;
}

.range-value {
  font-family: var(--cb-font-mono);
  font-size: 0.875rem;
  color: var(--cb-brand);
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}

.toggle-label {
  display: flex !important;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.toggle {
  display: none;
}

.toggle-slider {
  width: 44px;
  height: 24px;
  background: var(--vp-c-divider);
  border-radius: var(--cb-radius-full);
  position: relative;
  transition: all 0.2s ease;
}

.toggle-slider::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle:checked + .toggle-slider {
  background: var(--cb-brand);
}

.toggle:checked + .toggle-slider::after {
  left: 22px;
}

.toggle-text {
  font-size: 0.8125rem;
  color: var(--vp-c-text-2);
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem !important;
  font-weight: 400 !important;
  cursor: pointer;
}

.checkbox-label input {
  width: auto !important;
}

.field-description {
  font-size: 0.75rem;
  color: var(--vp-c-text-3);
  margin-top: 0.25rem;
  margin-bottom: 0;
}

.config-preview {
  background: #0f172a;
  display: flex;
  flex-direction: column;
}

.preview-header {
  padding: 0.625rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.preview-filename {
  font-size: 0.75rem;
  color: var(--cb-gray-500);
  font-family: var(--cb-font-mono);
}

.preview-code {
  flex: 1;
  margin: 0;
  padding: 1rem;
  overflow: auto;
  font-family: var(--cb-font-mono);
  font-size: 0.8125rem;
  line-height: 1.6;
}

.preview-code code {
  color: #e2e8f0;
}

:deep(.token-key) { color: #7dd3fc; }
:deep(.token-string) { color: #86efac; }
:deep(.token-number) { color: #fca5a5; }
:deep(.token-boolean) { color: #c4b5fd; }

@media (max-width: 768px) {
  .config-body {
    grid-template-columns: 1fr;
  }
  
  .config-form {
    border-right: none;
    border-bottom: 1px solid var(--vp-c-divider);
    max-height: 300px;
  }
  
  .config-preview {
    min-height: 200px;
  }
}
</style>
