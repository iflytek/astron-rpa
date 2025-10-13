import type { ShortCutManager } from '@rpa/shared/platform'
import type { ShortcutHandler } from '@tauri-apps/api/globalShortcut'
import { register, unregister, unregisterAll } from '@tauri-apps/api/globalShortcut'

const toolbarShortCut = ['Shift+F5', 'F5', 'F10', 'F9', 'F8', 'Shift+F10']

const TauriShortCut: ShortCutManager = {
  register: async (shortKey, handler: ShortcutHandler) => {
    await register(shortKey, handler)
  },
  unregister: async (shortKey) => {
    await unregister(shortKey)
  },
  unregisterAll: async () => {
    await unregisterAll()
  },
  regeisterToolbar: async () => {
    await TauriShortCut.unregisterAll()
    toolbarShortCut.forEach(shortKey =>
      TauriShortCut.register(shortKey, (sc: string) => {
        console.log(`toolbarShortCut: ${sc}`)
      }),
    )
  },
  regeisterFlow() {
    throw new Error('Method not implemented.')
  },
}

export default TauriShortCut
