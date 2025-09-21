<script setup lang="ts">
import { MenuOutlined } from '@ant-design/icons-vue'
import { computed, ref } from 'vue'

import { WINDOW_NAME } from '@/constants'
import { RECORD_EVENT } from '@/constants/record'
import { utilsManager, windowManager } from '@/platform'

import {
  emitToRecord,
  genMenuItems,
  MAX_HEIGHT,
  MAX_WIDTH,
  MIN_HEIGHT,
  MIN_WIDTH,
} from './utils'

interface W2WType {
  from: WINDOW_NAME // 来源窗口
  target: WINDOW_NAME // 目标窗口
  type: RECORD_EVENT // 类型
  data?: any // 数据
}

const open = ref(false)
const isWeb = ref(true)

const menuItems = computed(() => genMenuItems(isWeb.value))

utilsManager.listenEvent('w2w', async ({ from, target, type, data }: W2WType) => {
  if (from !== WINDOW_NAME.RECORD || target !== WINDOW_NAME.RECORD_MENU)
    return

  if (type === RECORD_EVENT.SHOW_MENU) {
    const { x, y } = data
    isWeb.value = data.isWeb ?? true
    await windowManager.setWindowSize({ width: MIN_WIDTH, height: MIN_HEIGHT })
    await windowManager.setWindowPosition(x + 10, y - 10 - MIN_HEIGHT)
    await windowManager.showWindow()
    await windowManager.setWindowAlwaysOnTop()
  }
  else if (type === RECORD_EVENT.HIDE_MENU) {
    await windowManager.hideWindow()
  }
})

async function openChange(visible: boolean) {
  console.log('openChange', visible)

  if (visible) {
    await windowManager.setWindowSize({ width: MAX_WIDTH, height: MAX_HEIGHT })
    emitToRecord(RECORD_EVENT.PAUSE_PICK)
    open.value = true
  }
  else {
    open.value = false
    await windowManager.setWindowSize({ width: MIN_WIDTH, height: MIN_HEIGHT })
    emitToRecord(RECORD_EVENT.RESUME_PICK)
  }

  await windowManager.setWindowAlwaysOnTop()
}

function handleClick(key: string) {
  emitToRecord(RECORD_EVENT.CLICK_ACTION, key)
  openChange(false)
}
</script>

<template>
  <a-dropdown :open="open" style="width: 256px" @open-change="openChange">
    <a-button
      size="small"
      type="primary"
      class="absolute top-0 left-0 inline-flex items-center justify-center"
      :style="{ width: `${MIN_WIDTH}px`, height: `${MIN_HEIGHT}px` }"
    >
      <template #icon>
        <MenuOutlined class="text-[12px]" />
      </template>
    </a-button>

    <template #overlay>
      <a-menu
        :items="menuItems"
        class="atom-menu"
        @click="handleClick($event.key as string)"
      />
    </template>
  </a-dropdown>
</template>

<style lang="scss">
.atom-menu {
  .ant-dropdown-menu-submenu-title {
    display: flex;
    align-items: center;
  }

  .ant-dropdown-menu-submenu-arrow {
    display: inline-flex;
  }
}
</style>
