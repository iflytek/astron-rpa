import type { ToolFileArtifact } from '@/components/AstronAssistant/tool-files'

interface ElectronLocalFileResult {
  textContent?: string
  dataUrl?: string
  mimeType?: string
  base64?: string
}

interface ElectronOpenClawBridge {
  readLocalFile?: (params: {
    path: string
    mode: 'text' | 'data-url'
  }) => Promise<ElectronLocalFileResult | undefined>
}

export interface LocalFilePreviewResult {
  kind: 'text' | 'pdf'
  textContent?: string
  dataUrl?: string
  source: 'inline' | 'electron'
}

function getElectronOpenClawBridge(): ElectronOpenClawBridge | undefined {
  return (window as any)?.electron?.openclaw
}

function normalizeDataUrl(result: ElectronLocalFileResult | undefined): string | undefined {
  if (!result)
    return undefined

  if (result.dataUrl?.trim())
    return result.dataUrl.trim()

  if (!result.base64?.trim())
    return undefined

  const mimeType = result.mimeType?.trim() || 'application/octet-stream'
  return `data:${mimeType};base64,${result.base64.trim()}`
}

export async function loadLocalFilePreview(artifact: ToolFileArtifact): Promise<LocalFilePreviewResult> {
  if (artifact.previewKind === 'text' && artifact.content?.trim()) {
    return {
      kind: 'text',
      textContent: artifact.content,
      source: 'inline',
    }
  }

  const bridge = getElectronOpenClawBridge()
  if (!bridge?.readLocalFile) {
    throw new Error(
      artifact.previewKind === 'pdf'
        ? '当前浏览器模式不能直接读取本地 PDF，请在 Electron 中打开。'
        : '当前浏览器模式不能直接读取本地文件内容。',
    )
  }

  if (artifact.previewKind === 'pdf') {
    const result = await bridge.readLocalFile({
      path: artifact.path,
      mode: 'data-url',
    })
    const dataUrl = normalizeDataUrl(result)
    if (!dataUrl)
      throw new Error('无法读取 PDF 预览内容。')

    return {
      kind: 'pdf',
      dataUrl,
      source: 'electron',
    }
  }

  const result = await bridge.readLocalFile({
    path: artifact.path,
    mode: 'text',
  })
  const textContent = result?.textContent?.trim()
  if (!textContent)
    throw new Error('无法读取文件文本内容。')

  return {
    kind: 'text',
    textContent,
    source: 'electron',
  }
}
