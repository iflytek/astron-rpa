<template>
  <VueMonacoEditor
    class="monaco-editor--wrapper"
    :value="code"
    :height="height"
    language="python"
    :options="options"
    :theme="theme"
    @mount="handleEditorDidMount"
    @change="handleChange"
  />
</template>

<script setup lang="ts">
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import type * as monaco from 'monaco-editor/esm/vs/editor/editor.api'
import type { Diagnostic, Range } from 'vscode-languageserver-types'
import { ref, watch } from 'vue'

import type { LspClient } from './LspClient'
import { convertRange, registerModel, setFileMarkers } from './utils'

type IMonacoEditor = typeof monaco

interface Props {
  height?: string
  code?: string
  diagnostics?: Diagnostic[]
  lspClient: LspClient
  theme?: string
}

interface Emits {
  (e: 'updateCode', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  height: '100%',
  code: '',
  diagnostics: () => [],
  theme: 'vs'
})

const emit = defineEmits<Emits>()

const editorRef = ref<monaco.editor.IStandaloneCodeEditor>()
const monacoRef = ref<IMonacoEditor>()

const options: monaco.editor.IStandaloneEditorConstructionOptions = {
  selectOnLineNumbers: true,
  minimap: { enabled: false },
  fixedOverflowWidgets: true,
  tabCompletion: 'on',
  hover: { enabled: true },
  scrollBeyondLastLine: true,
  scrollBeyondLastColumn: 10,
  autoClosingOvertype: 'always',
  autoSurround: 'quotes',
  autoIndent: 'full',
  showUnused: true,
  wordBasedSuggestions: 'currentDocument',
  overviewRulerLanes: 0,
  renderWhitespace: 'none',
  guides: {
    indentation: false,
  },
  padding: {
    top: 8,
    bottom: 8,
  },
  renderLineHighlight: 'none',
  scrollbar: {
    verticalScrollbarSize: 6,
    horizontalScrollbarSize: 6,
  },
}

watch(() => props.diagnostics, (newDiagnostics) => {
  if (monacoRef.value && editorRef.value) {
    const model = editorRef.value.getModel()
    model && setFileMarkers(monacoRef.value, model, newDiagnostics)
  }
}, { immediate: true, flush: 'post' })

const handleEditorDidMount = (editor: monaco.editor.IStandaloneCodeEditor, monacoInstance: IMonacoEditor) => {
  editorRef.value = editor
  monacoRef.value = monacoInstance

  editor.focus()

  const model = editorRef.value.getModel()
  // Register the editor and the LSP Client so they can be accessed
  // by the hover provider, etc.
  model && registerModel(model, props.lspClient)
}

const handleChange = (value: string) => {
  emit('updateCode', value)
}

const focus = () => {
  if (editorRef.value) {
    editorRef.value.focus()
  }
}

const selectRange = (range: Range) => {
  if (editorRef.value) {
    const monacoRange = convertRange(range)
    editorRef.value.setSelection(monacoRange)
    editorRef.value.revealLineInCenterIfOutsideViewport(monacoRange.startLineNumber)
  }
}

defineExpose({ focus, selectRange })
</script>
