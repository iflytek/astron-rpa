import { loader } from '@guolao/vue-monaco-editor'
import * as monaco from 'monaco-editor'
import type { IRange } from 'monaco-editor'
import type {
  CompletionItem,
  Diagnostic,
  Range,
} from 'vscode-languageserver-types'
import {
  CompletionItemKind,
  DiagnosticSeverity,
  InsertReplaceEdit,
  TextDocumentEdit,
} from 'vscode-languageserver-types'

import type { LspClient } from './LspClient'

interface RegisteredModel {
  model: monaco.editor.ITextModel
  lspClient: LspClient
}

const registeredModels: RegisteredModel[] = []

// https://github.com/imguolao/monaco-vue/blob/main/README.zh-CN.md#cdn
// loader.config({
//   'paths': {
//     vs: 'https://unpkg.com/monaco-editor@0.52.2/min/vs',
//   },
//   'vs/nls': {
//     availableLanguages: { '*': 'zh-cn' },
//   },
// })

// 配置从 `node_modules` 中加载 monaco-editor
loader.config({ monaco })

loader
  .init()
  .then((monaco) => {
    monaco.languages.registerHoverProvider('python', {
      provideHover: handleHoverRequest,
    })
    monaco.languages.registerSignatureHelpProvider('python', {
      provideSignatureHelp: handleSignatureHelpRequest,
      signatureHelpTriggerCharacters: ['(', ','],
    })
    monaco.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: handleProvideCompletionRequest,
      resolveCompletionItem: handleResolveCompletionRequest,
      triggerCharacters: ['.', '[', '"', '\''],
    })
    monaco.languages.registerRenameProvider('python', {
      provideRenameEdits: handleRenameRequest,
    })
  })
  .catch(error => console.error('An error occurred during initialization of Monaco: ', error))

async function handleHoverRequest(
  model: monaco.editor.ITextModel,
  position: monaco.Position,
): Promise<monaco.languages.Hover | null> {
  const lspClient = getLspClientForModel(model)

  if (!lspClient) {
    return null
  }

  try {
    const hoverInfo = await lspClient.getHoverForPosition(model.getValue(), {
      line: position.lineNumber - 1,
      character: position.column - 1,
    })

    return {
      contents: [
        {
          value: hoverInfo!.contents.value,
        },
      ],
      range: convertRange(hoverInfo!.range),
    }
  }
  catch {
    return null
  }
}

async function handleRenameRequest(
  model: monaco.editor.ITextModel,
  position: monaco.Position,
  newName: string,
): Promise<monaco.languages.WorkspaceEdit | null> {
  const lspClient = getLspClientForModel(model)
  if (!lspClient) {
    return null
  }

  try {
    const renameEdits = await lspClient.getRenameEditsForPosition(
      model.getValue(),
      {
        line: position.lineNumber - 1,
        character: position.column - 1,
      },
      newName,
    )

    const edits: monaco.languages.IWorkspaceTextEdit[] = []

    if (renameEdits?.documentChanges) {
      for (const docChange of renameEdits.documentChanges) {
        if (TextDocumentEdit.is(docChange)) {
          for (const textEdit of docChange.edits) {
            edits.push({
              resource: model.uri,
              versionId: undefined,
              textEdit: {
                range: convertRange(textEdit.range),
                text: textEdit.newText,
              },
            })
          }
        }
      }
    }

    return { edits }
  }
  catch {
    return null
  }
}

async function handleSignatureHelpRequest(
  model: monaco.editor.ITextModel,
  position: monaco.Position,
): Promise<monaco.languages.SignatureHelpResult | null> {
  const lspClient = getLspClientForModel(model)
  if (!lspClient) {
    return null
  }

  try {
    const sigInfo = await lspClient.getSignatureHelpForPosition(model.getValue(), {
      line: position.lineNumber - 1,
      character: position.column - 1,
    })

    return {
      value: {
        signatures: sigInfo!.signatures.map((sig) => {
          return {
            label: sig.label,
            documentation: sig.documentation,
            parameters: sig.parameters!,
            activeParameter: sig.activeParameter,
          }
        }),
        activeSignature: sigInfo!.activeSignature ?? 0,
        activeParameter: sigInfo!.activeParameter!,
      },
      dispose: () => { },
    }
  }
  catch {
    return null
  }
}

async function handleProvideCompletionRequest(
  model: monaco.editor.ITextModel,
  position: monaco.Position,
): Promise<monaco.languages.CompletionList | null> {
  const lspClient = getLspClientForModel(model)
  if (!lspClient) {
    return null
  }

  try {
    const completionInfo = await lspClient.getCompletionForPosition(model.getValue(), {
      line: position.lineNumber - 1,
      character: position.column - 1,
    })

    return {
      suggestions: completionInfo!.items.map((item) => {
        return convertCompletionItem(item, model)
      }),
      incomplete: completionInfo!.isIncomplete,
      dispose: () => { },
    }
  }
  catch {
    return null
  }
}

async function handleResolveCompletionRequest(
  item: monaco.languages.CompletionItem,
): Promise<monaco.languages.CompletionItem | null> {
  const model = (item as any).model as monaco.editor.ITextModel | undefined
  const original = (item as any).__original as CompletionItem | undefined
  if (!model || !original) {
    return null
  }

  const lspClient = getLspClientForModel(model)
  if (!lspClient) {
    return null
  }

  try {
    const result = await lspClient.resolveCompletionItem(original)
    return convertCompletionItem(result!)
  }
  catch {
    return null
  }
}

function convertCompletionItem(
  item: CompletionItem,
  model?: monaco.editor.ITextModel,
): monaco.languages.CompletionItem {
  const converted: monaco.languages.CompletionItem = {
    label: item.label,
    kind: convertCompletionItemKind(item.kind),
    tags: item.tags,
    detail: item.detail,
    documentation: item.documentation,
    sortText: item.sortText,
    filterText: item.filterText,
    preselect: item.preselect,
    insertText: item.label,
    range: undefined as unknown as IRange,
  }

  if (item.textEdit) {
    converted.insertText = item.textEdit.newText
    if (InsertReplaceEdit.is(item.textEdit)) {
      converted.range = {
        insert: convertRange(item.textEdit.insert),
        replace: convertRange(item.textEdit.replace),
      }
    }
    else {
      converted.range = convertRange(item.textEdit.range)
    }
  }

  if (item.additionalTextEdits) {
    converted.additionalTextEdits = item.additionalTextEdits.map((edit) => {
      return {
        range: convertRange(edit.range),
        text: edit.newText,
      }
    })
  }

  // Stash a few additional pieces of information.
  (converted as any).__original = item
  if (model) {
    (converted as any).model = model
  }

  return converted
}

function convertCompletionItemKind(
  itemKind?: CompletionItemKind,
): monaco.languages.CompletionItemKind {
  switch (itemKind) {
    case CompletionItemKind.Constant:
      return monaco.languages.CompletionItemKind.Constant

    case CompletionItemKind.Variable:
      return monaco.languages.CompletionItemKind.Variable

    case CompletionItemKind.Function:
      return monaco.languages.CompletionItemKind.Function

    case CompletionItemKind.Field:
      return monaco.languages.CompletionItemKind.Field

    case CompletionItemKind.Keyword:
      return monaco.languages.CompletionItemKind.Keyword

    default:
      return monaco.languages.CompletionItemKind.Reference
  }
}

function convertSeverity(severity?: DiagnosticSeverity): monaco.MarkerSeverity {
  switch (severity) {
    case DiagnosticSeverity.Warning:
      return monaco.MarkerSeverity.Warning

    case DiagnosticSeverity.Information:
      return monaco.MarkerSeverity.Info

    case DiagnosticSeverity.Hint:
      return monaco.MarkerSeverity.Hint

    case DiagnosticSeverity.Error:
    default:
      return monaco.MarkerSeverity.Error
  }
}

export function convertRange(range: Range): monaco.IRange {
  return {
    startLineNumber: range.start.line + 1,
    startColumn: range.start.character + 1,
    endLineNumber: range.end.line + 1,
    endColumn: range.end.character + 1,
  }
}

export function setFileMarkers(
  monacoInstance: any,
  model: monaco.editor.ITextModel,
  diagnostics: Diagnostic[],
) {
  const markers: monaco.editor.IMarkerData[] = []

  diagnostics.forEach((diag) => {
    const markerData: monaco.editor.IMarkerData = {
      ...convertRange(diag.range),
      severity: convertSeverity(diag.severity),
      message: diag.message,
    }

    if (diag.tags) {
      markerData.tags = diag.tags
    }
    markers.push(markerData)
  })

  monacoInstance.editor.setModelMarkers(model, 'pyright', markers)
}

export function registerModel(model: monaco.editor.ITextModel, lspClient: LspClient) {
  if (findRegisteredModel(model)) {
    return
  }

  registeredModels.push({ model, lspClient })
}

function findRegisteredModel(model: monaco.editor.ITextModel) {
  // TODO: 不知道什么原因，直接比对 model 无法找到对应的实例，需要使用 uri 来匹配
  return registeredModels.find(m => m.model.uri.toString() === model.uri.toString())
}

function getLspClientForModel(model: monaco.editor.ITextModel): LspClient | undefined {
  return findRegisteredModel(model)?.lspClient
}
