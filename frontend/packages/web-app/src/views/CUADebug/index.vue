<script setup lang="ts">
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import CUADebugModal from '@/views/Arrange/components/atomForm/modals/CUADebugModal.vue'

interface DebugWindowState {
  atomId?: string
  atomSnapshot?: RPA.Atom
  currentLine?: number
  initialInstruction?: string
  projectId?: string
  processId?: string
  project?: {
    id: string
    name: string
    version: number
  }
}

const searchParams = new URLSearchParams(window.location.search)
const stateRaw = searchParams.get('state') || '{}'

let state: DebugWindowState = {}
try {
  state = JSON.parse(decodeURIComponent(stateRaw))
}
catch (error) {
  console.error('Failed to parse CUA debug window state:', error)
}
</script>

<template>
  <ConfigProvider>
    <CUADebugModal
      :atom-id="state.atomId || ''"
      :atom-snapshot="state.atomSnapshot"
      :current-line="state.currentLine || 0"
      :initial-instruction="state.initialInstruction || ''"
      :project-id="state.projectId || state.project?.id || ''"
      :process-id="state.processId || ''"
      :project="state.project"
    />
  </ConfigProvider>
</template>
