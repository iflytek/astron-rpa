<script setup lang="ts">
import { onMounted, toRaw, useTemplateRef } from 'vue'
import { useElementSize } from '@vueuse/core'

import { WINDOW_NAME } from '@/constants'
import { windowManager } from '@/platform'
import type { AnyObj } from '@/types/common'
import type { DialogOption } from '@/views/Arrange/components/customDialog/types'
import UserFormDialog from '@/views/Arrange/components/customDialog/components/userFormDialog.vue'

import { transformData } from './utils'

const userFormRef = useTemplateRef<HTMLDivElement>('userFormRef')
const useFormSize = useElementSize(userFormRef)

async function resizeWindow() {
  const formHeight = useFormSize.height.value
  // 计算设置自定义对话框窗口高度，实现高度随动
  const { offsetWidth: bodyWidth } = document.body
  // 判断计算高度是否超过了所在屏幕高度
  const screenWorkArea = await windowManager.getScreenWorkArea()
  const resHeight = Math.min(formHeight, screenWorkArea.height)
  await windowManager.setWindowSize({ width: bodyWidth, height: resHeight })
  await windowManager.showWindow()
}

const targetInfo = new URL(location.href).searchParams
const windowOption = transformData(JSON.parse(targetInfo.get('option'))) as DialogOption
const replyBaseData = JSON.parse(targetInfo.get('reply') || '{}') ?? {}

onMounted(() => resizeWindow())

function handleClose() {
  windowManager.closeWindow()
}

function handleSave(data: AnyObj) {
  windowManager.emitTo({
    from: WINDOW_NAME.USERFORM,
    target: WINDOW_NAME.MAIN,
    type: 'userFormSave',
    data: { ...replyBaseData, data: toRaw(data) },
  })
}
</script>

<template>
  <div ref="userFormRef">
    <UserFormDialog draggable :option="windowOption" @close="handleClose" @save="handleSave" />
  </div>
</template>
