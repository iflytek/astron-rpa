import { Icon } from '@rpa/components'
import type { VNode } from 'vue'
import { h } from 'vue'

import { WINDOW_NAME } from '@/constants'
import type { RECORD_EVENT } from '@/constants/record'
import { DesktopRecordActionType, RecordActionMap, RecordActionType } from '@/constants/record'
import { windowManager } from '@/platform'

export const MIN_WIDTH = 20
export const MIN_HEIGHT = 20
export const MAX_WIDTH = 400
export const MAX_HEIGHT = 400

const genIcon = (name: string) => h(Icon, { name })

export interface ItemProps {
  key: string
  icon: VNode
  label: string
  disabled: boolean
  children?: ItemProps[]
}

export function genMenuItems(isWeb: boolean): ItemProps[] {
  function genItem(key: RecordActionType, children?: ItemProps[]) {
    const withEnableItem = children?.some(child => child.disabled === false)

    return {
      key,
      icon: genIcon(RecordActionMap[key].icon),
      label: RecordActionMap[key].label,
      disabled: !withEnableItem && !isWeb && !DesktopRecordActionType[key],
      children,
    }
  }

  return [
    genItem(RecordActionType.GET_ELEMENT_INFO, [
      genItem(RecordActionType.GET_ELEMENT_TEXT),
      genItem(RecordActionType.GET_ELEMENT_CODE),
      genItem(RecordActionType.GET_ELEMENT_LINK),
      genItem(RecordActionType.GET_ELEMENT_ATTR),
    ]),
    genItem(RecordActionType.INPUT),
    genItem(RecordActionType.MOUSE_MOVE),
    genItem(RecordActionType.CLICK, [
      genItem(RecordActionType.CLICK_LEFT),
      genItem(RecordActionType.CLICK_LEFT_RIGHT),
      genItem(RecordActionType.CLICK_RIGHT),
    ]),
    genItem(RecordActionType.WAIT_ELEMENT, [
      genItem(RecordActionType.WAIT_ELEMENT_SHOW),
      genItem(RecordActionType.WAIT_ELEMENT_HIDE),
    ]),
    genItem(RecordActionType.SNAPSHOT),
  ]
}

export function emitToRecord(type: RECORD_EVENT, data = '') {
  windowManager.emitTo({
    type,
    target: WINDOW_NAME.RECORD,
    from: WINDOW_NAME.RECORD_MENU,
    data,
  })
}
