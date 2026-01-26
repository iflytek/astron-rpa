<template>
  <MonacoEditor
    :height="height"
    :lsp-client="lspClient"
    :code="code"
    :diagnostics="diagnostics"
    :theme="isDark ? 'vs-dark' : 'vs'"
    @update-code="handleUpdate"
  />
</template>

<script setup lang="ts">
import type { Diagnostic } from 'vscode-languageserver-types'
import { DiagnosticSeverity } from 'vscode-languageserver-types'
import { ref, watch } from 'vue'

import { LspClient } from './LspClient'
import MonacoEditor from './MonacoEditor.vue'
import type { EditorSettings } from './Settings'

interface Props {
  projectId: string
  height?: string
  value?: string
  baseUrl?: string
  isDark?: boolean
}

interface Emits {
  (e: 'update:value', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  height: '100%',
  value: '',
  isDark: false
})

const emit = defineEmits<Emits>()

const code = ref<string>(props.value)
const settings = ref<EditorSettings>({ locale: 'zh', projectId: props.projectId })
const diagnostics = ref<Diagnostic[]>([])

const lspClient = new LspClient(props.value, props.baseUrl)

lspClient.requestNotification({
  onDiagnostics: (_diagnostics: Diagnostic[]) => {
    diagnostics.value = _diagnostics
  },
  onError: (message: string) => {
    diagnostics.value = [
      {
        message: `An error occurred when attempting to contact the pyright web service\n    ${message}`,
        severity: DiagnosticSeverity.Error,
        range: {
          start: { line: 0, character: 0 },
          end: { line: 0, character: 0 },
        },
      },
    ]
  },
  onWaitingForDiagnostics: (isWaiting) => {
    console.log('isWaitingForResponse: ', isWaiting)
  },
})

const handleUpdate = (codeText: string) => {
  code.value = codeText
  lspClient.updateCode(codeText)
  emit('update:value', codeText)
}

watch(settings, (newSettings) => {
  lspClient.updateSettings(newSettings)
}, { immediate: true })

watch(() => props.value, (newCode) => {
  if (newCode === code.value)
    return

  code.value = newCode
  lspClient.updateCode(newCode)
})
</script>
