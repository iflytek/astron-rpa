<script setup lang="ts">
import { CheckOutlined, CloseOutlined, ZoomInOutlined, ZoomOutOutlined } from '@ant-design/icons-vue'
import { Button } from 'ant-design-vue'
import { ref } from 'vue'

import ConfigProvider from '@/components/ConfigProvider/index.vue'
import { WINDOW_NAME } from '@/constants'
import { SMART_COMP_PICK_EVENT } from '@/constants/smartCompPick'
import { utilsManager, windowManager } from '@/platform'

import {
  emitToMain,
  MAX_HEIGHT,
  MAX_WIDTH,
} from './utils'

interface W2WType {
  from: WINDOW_NAME // 来源窗口
  target: WINDOW_NAME // 目标窗口
  type: SMART_COMP_PICK_EVENT // 类型
  data?: any // 数据
}

const showErrorDialog = ref(false)
const errorMessage = ref('当前仅支持网页自动化')

utilsManager.listenEvent('w2w', async ({ from, target, type, data }: W2WType) => {
  if (from !== WINDOW_NAME.MAIN || target !== WINDOW_NAME.SMART_COMP_PICK_MENU)
    return

  if (type === SMART_COMP_PICK_EVENT.SHOW_MENU) {
    const { x, y } = data
    await windowManager.setWindowSize({ width: MAX_WIDTH, height: MAX_HEIGHT })
    await windowManager.setWindowPosition(x + 2, y + 2)
    await windowManager.showWindow()
    await windowManager.setWindowAlwaysOnTop()
  }
  else if (type === SMART_COMP_PICK_EVENT.HIDE_MENU) {
    await windowManager.closeWindow()
  }
  else if (type === SMART_COMP_PICK_EVENT.SHOW_ERROR_DIALOG) {
    // 显示错误对话框
    errorMessage.value = data?.errorMsg || '当前仅支持网页自动化'
    showErrorDialog.value = true
    await windowManager.setWindowSize({ width: 368, height: 140 })
    await windowManager.centerWindow()
    await windowManager.showWindow()
    await windowManager.setWindowAlwaysOnTop()
  }
})

async function handleErrorDialog() {
  showErrorDialog.value = false
  emitToMain(SMART_COMP_PICK_EVENT.ERROR_DIALOG_CONFIRM)
  await windowManager.setWindowSize({ width: MAX_WIDTH, height: MAX_HEIGHT })
  await windowManager.setWindowPosition(-999, -999)
}

function handleZoomIn() {
  emitToMain(SMART_COMP_PICK_EVENT.ZOOM_IN)
}

function handleZoomOut() {
  emitToMain(SMART_COMP_PICK_EVENT.ZOOM_OUT)
}

function handleConfirm() {
  emitToMain(SMART_COMP_PICK_EVENT.CONFIRM)
}

function handleCancel() {
  emitToMain(SMART_COMP_PICK_EVENT.CANCEL)
}
</script>

<template>
  <ConfigProvider>
    <div v-if="!showErrorDialog" class="p-2 h-full bg-bg-elevated shadow-md border border-primary rounded">
      <div class="w-full flex items-center justify-between">
        <Button
          size="small"
          type="primary"
          class="flex items-center justify-center"
          @click="handleZoomIn"
        >
          <template #icon>
            <ZoomInOutlined />
          </template>
        </Button>
        <Button
          size="small"
          type="primary"
          class="flex items-center justify-center"
          @click="handleZoomOut"
        >
          <template #icon>
            <ZoomOutOutlined />
          </template>
        </Button>
        <Button
          size="small"
          type="primary"
          class="flex items-center justify-center"
          danger
          @click="handleCancel"
        >
          <template #icon>
            <CloseOutlined />
          </template>
        </Button>
        <Button
          size="small"
          type="primary"
          class="flex items-center justify-center"
          @click="handleConfirm"
        >
          <template #icon>
            <CheckOutlined />
          </template>
        </Button>
      </div>
    </div>

    <div v-if="showErrorDialog" class="h-full flex flex-col border border-[#000000]/[.1] dark:border-[#FFFFFF]/[.16 bg-bg-elevated px-6 py-5 rounded-lg">
      <div class="flex items-center">
        <rpa-icon name="error" size="16" />
        <span class="ml-2 mr-auto font-medium text-[16px]">拾取元素失败</span>
        <rpa-hint-icon name="close" enable-hover-bg @click="handleErrorDialog" />
      </div>
      <span class="mt-2 mb-3">{{ errorMessage }}</span>
      <div class="flex items-center gap-2 justify-end">
        <a-button @click="handleErrorDialog">
          取消
        </a-button>
        <a-button type="primary" @click="handleErrorDialog">
          确定
        </a-button>
      </div>
    </div>
  </ConfigProvider>
</template>
