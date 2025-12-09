/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME: string
  readonly VITE_APP_WS_URL: string
  readonly VITE_APP_AUTHOR: string
  readonly VITE_APP_HOMEPAGE: string
  readonly VITE_FIREFOXID: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
