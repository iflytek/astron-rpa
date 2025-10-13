/// <reference types="vite/client" />
/// <reference types="@rpa/shared/platform" />

interface ViteTypeOptions {
  // 添加这行代码，你就可以将 ImportMetaEnv 的类型设为严格模式，
  // 这样就不允许有未知的键值了。
  // strictImportMetaEnv: unknown
}

interface ImportMetaEnv {
  readonly VITE_SENTRY_DSN: string
  // 更多环境变量...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
