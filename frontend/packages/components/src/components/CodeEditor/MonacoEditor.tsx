import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import type * as monaco from 'monaco-editor/esm/vs/editor/editor.api'
import type { Diagnostic, Range } from 'vscode-languageserver-types'
import type { PropType } from 'vue'
import { defineComponent, ref, watch } from 'vue'

import type { LspClient } from './LspClient'
import { convertRange, registerModel, setFileMarkers } from './utils'

type IMonacoEditor = typeof monaco

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

export const MonacoEditor = defineComponent({
  name: 'MonacoEditor',
  props: {
    height: {
      type: String,
      default: '100%',
    },
    code: {
      type: String,
      default: '',
    },
    diagnostics: {
      type: Array as PropType<Diagnostic[]>,
      default: () => [],
    },
    lspClient: {
      type: Object as PropType<LspClient>,
      required: true,
    },
    theme: {
      type: String,
      default: 'vs',
    },
  },
  emits: { updateCode: (_value: string) => true },
  setup(props, { expose, emit }) {
    const editorRef = ref<monaco.editor.IStandaloneCodeEditor>()
    const monacoRef = ref<IMonacoEditor>()

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

    expose({ focus, selectRange })

    return () => (
      <VueMonacoEditor
        class="monaco-editor--wrapper"
        value={props.code}
        height={props.height}
        language="python"
        options={options}
        theme={props.theme}
        onMount={handleEditorDidMount}
        onChange={value => emit('updateCode', value)}
      />
    )
  },
})
