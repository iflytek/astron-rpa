import type { ClipboardManager } from '@rpa/shared/platform'

const ClipBoard: ClipboardManager = {
  async writeClipboardText(text: string) {
    navigator.clipboard.writeText(text)
  },
  async readClipboardText() {
    return navigator.clipboard.readText()
  },
}

export default ClipBoard
