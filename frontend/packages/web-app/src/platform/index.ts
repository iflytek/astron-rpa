import type { ClipboardManager, ShortCutManager, UpdaterManager, UtilsManager, WindowManager } from '@rpa/shared/platform'

import ClipBoard from './clipboard'
import ShortCut from './short-cut'
import Updater from './updater'
import Utils from './utils-manager'
import Window from './window-manager'

export const updaterManager: UpdaterManager = window.UpdaterManager ?? Updater
export const shortCutManager: ShortCutManager = window.ShortCutManager ?? ShortCut
export const clipboardManager: ClipboardManager = window.ClipboardManager ?? ClipBoard
export const utilsManager: UtilsManager = window.UtilsManager ?? Utils
export const windowManager: WindowManager = window.WindowManager ?? new Window()

export const isBrowser = utilsManager.getAppEnv() === 'browser'

windowManager.hideDecorations()
