import { WINDOW_NAME } from '@/constants'
import type { SMART_COMP_PICK_EVENT } from '@/constants/smartCompPick'
import { windowManager } from '@/platform'

export const MIN_WIDTH = 20
export const MIN_HEIGHT = 20
export const MAX_WIDTH = 160
export const MAX_HEIGHT = 40

export function emitToMain(type: SMART_COMP_PICK_EVENT, data = '') {
  windowManager.emitTo({
    type,
    target: WINDOW_NAME.MAIN,
    from: WINDOW_NAME.SMART_COMP_PICK_MENU,
    data,
  })
}
