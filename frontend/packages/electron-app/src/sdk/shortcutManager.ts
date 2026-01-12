import type { ShortCutManager } from '@rpa/shared/platform'

class ElectronShortCut implements ShortCutManager {
  public baseShortCut = ['CommandOrControl+F']
  public toolbarShortCut = ['Shift+F5', 'F5', 'F10', 'F9', 'F8', 'Shift+F10']
  private globalShortcut = window.electron.globalShortcut

  register(shortKey: string, handler: (...args) => void) {
    this.globalShortcut.register(shortKey, handler)
  }

  unregister(shortKey: string) {
    this.globalShortcut.unregister(shortKey)
  }

  unregisterAll() {
    this.globalShortcut.unregisterAll()
  }

  regeisterToolbar() {
    this.unregisterAll()
    this.toolbarShortCut.forEach(shortKey =>
      this.register(shortKey, (sc: string) => {
        console.log(`toolbarShortCut: ${sc}`)
      }),
    )
  }

  regeisterFlow(): void {}
}

export default ElectronShortCut
