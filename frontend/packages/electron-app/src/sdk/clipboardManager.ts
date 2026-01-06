import type { ClipboardManager } from '@rpa/shared/platform'

const { clipboard } = window.electron

function readClipboardText() {
  return new Promise<string>((resolve) => {
    const text = clipboard.readText()
    resolve(text)
  })
}

function writeClipboardText(text: string) {
  return new Promise<void>((resolve) => {
    clipboard.writeText(text)
    resolve()
  })
}

const ClipboardManager: ClipboardManager = {
  readClipboardText,
  writeClipboardText,
}

export default ClipboardManager
