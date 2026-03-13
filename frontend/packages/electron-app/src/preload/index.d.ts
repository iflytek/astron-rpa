import type { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI & {
      openclaw?: {
        getToken: () => Promise<string | undefined>
      }
    }
    api: unknown
  }
}
