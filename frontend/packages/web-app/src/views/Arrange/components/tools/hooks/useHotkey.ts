import { onBeforeUnmount } from 'vue'

import { registerHotkey, unregisterHotkey } from '@/utils/registerHotkeys'

import type { Fun } from '@/types/common'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useHotkey(toolsLeft: ArrangeTools[], hotkeyCallback: Fun) {
  const resister = (hotkeyList: ArrangeTools[]) => {
    hotkeyList.forEach((item) => {
      item.hotkey && registerHotkey(item.hotkey, () => {
        // 注册时的hotkey的数据和实时变化的toolsLeft的数据可能不一致，所以需要重新获取
        hotkeyCallback(toolsLeft.find(i => i.key === item.key))
      })
    })
  }

  onBeforeUnmount(() => {
    toolsLeft.forEach((item) => {
      item.hotkey && unregisterHotkey(item.hotkey)
    })
  })

  resister(toolsLeft)
}
