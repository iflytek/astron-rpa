/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly MAIN_VITE_PRODUCT_NAME: string
  readonly MAIN_VITE_PRODUCT_ID: string
  readonly MAIN_VITE_SHORTCUT_NAME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
