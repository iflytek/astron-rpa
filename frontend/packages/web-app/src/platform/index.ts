import type { ClipboardManager, ShortCutManager, UpdaterManager, UtilsManager, WindowManager } from '@rpa/shared/platform'

import ClipBoard from './clipboard'
import ShortCut from './short-cut'
import Updater from './updater'
import Utils from './utils-manager'
import Window from './window-manager'

export const updaterManager: UpdaterManager = window.UpdaterManager ?? Updater
export const shortCutManager: ShortCutManager = window.ShortCutManager ?? ShortCut
export const clipboardManager: ClipboardManager = window.ClipboardManager ?? ClipBoard
// TODO: 这里的 window.UtilsManager 类型不对，先断言为 UtilsManager 类型
export const utilsManager: UtilsManager = window.UtilsManager as UtilsManager ?? Utils
export const windowManager: WindowManager = window.WindowManager ?? new Window()

export const isBrowser = utilsManager.getAppEnv() === 'browser'

export type { WindowPosition, CreateWindowOptions } from '@rpa/shared/platform'

windowManager.hideDecorations()
