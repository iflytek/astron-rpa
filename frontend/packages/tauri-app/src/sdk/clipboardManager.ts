import { readText, writeText } from '@tauri-apps/api/clipboard'

async function readClipboardText() {
  const text = await readText()
  return text || ''
}

async function writeClipboardText(text: string) {
  writeText(text)
}

const ClipboardManager = {
  readClipboardText,
  writeClipboardText,
}

export default ClipboardManager
