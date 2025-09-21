import type { Diagnostic } from 'vscode-languageserver-types'
import { DiagnosticSeverity } from 'vscode-languageserver-types'
import { defineComponent, ref, watch } from 'vue'

import { LspClient } from './LspClient'
import { MonacoEditor } from './MonacoEditor'
import type { EditorSettings } from './Settings'

export const CodeEditor = defineComponent({
  name: 'CodeEditor',
  props: {
    projectId: {
      type: String,
      required: true,
    },
    height: {
      type: String,
      default: '100%',
    },
    value: {
      type: String,
      default: '',
    },
    baseUrl: String,
    isDark: Boolean,
  },
  emits: { 'update:value': (_value: string) => true },
  setup(props, { emit }) {
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

    return () => (
      <MonacoEditor
        height={props.height}
        lspClient={lspClient}
        code={code.value}
        diagnostics={diagnostics.value}
        theme={props.isDark ? 'vs-dark' : 'vs'}
        onUpdateCode={handleUpdate}
      />
    )
  },
})
