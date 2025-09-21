// 全局类型声明文件
// 这个文件确保全局类型在所有使用 @rpa/types 的 packages 中生效

import type {
  ClipboardManager,
  ShortCutManager,
  UpdaterManager,
  UtilsManager,
  WindowManager,
} from './index'

declare global {
  interface Window {
    WindowManager?: WindowManager
    ClipboardManager?: ClipboardManager
    UtilsManager?: UtilsManager
    ShortCutManager?: ShortCutManager
    UpdaterManager?: UpdaterManager
  }
}

// 确保这个文件被当作模块处理
export {}
