<script setup lang="ts">
import type { Rule } from 'ant-design-vue/es/form'
import { clamp } from 'lodash-es'
import { onMounted, toRaw } from 'vue'

import { WINDOW_NAME } from '@/constants'
import { utilsManager, windowManager } from '@/platform'
import type { AnyObj } from '@/types/common'
import type { DialogOption } from '@/views/Arrange/components/customDialog/types'

import UserFormDialog from '@/views/Arrange/components/customDialog/components/userFormDialog.vue'

const PICKER_MIN_HEIGHT = 340
const OTHER_MIN_HEIGHT = 200

function getPasswordRules(title: string) {
  return [
    {
      validator: (_rule: Rule, value: string) => {
        if (value.length < 4 || value.length > 16) {
          // eslint-disable-next-line prefer-promise-reject-errors
          return Promise.reject(`${title}请输入4-16位字符`)
        }
        return Promise.resolve()
      },
      trigger: 'change',
    },
  ]
}

// 定义基础对话框数据转换方法
function transformBasic(data: AnyObj): DialogOption {
  // 获取用户表单选项
  function getUserFormOption(data) {
    let rules = null
    switch (data.key) {
      case 'Dialog.select_box':
        return {
          dialogFormType: data.select_type === 'multi' ? 'MULTI_SELECT' : 'SINGLE_SELECT',
          label: data.options_title,
          options: data?.options?.map((op) => {
            return {
              label: op.value,
              value: op.value,
            }
          }) || [],
          defaultValue: data.select_type === 'multi' ? [] : '',
        }
      case 'Dialog.input_box':
        if (data.input_type !== 'text') {
          rules = getPasswordRules(data.input_title)
        }
        return {
          dialogFormType: data.input_type === 'text' ? 'INPUT' : 'PASSWORD',
          label: data.input_title,
          defaultValue: data.default_input,
          rules,
        }
      case 'Dialog.select_time_box':
        return {
          dialogFormType: data.time_type === 'time' ? 'DATEPICKER' : 'RANGERPICKER',
          label: data.input_title,
          format: data.time_format,
          defaultValue: data.time_type === 'time' ? data.default_time : data.default_time_range,
        }
      case 'Dialog.select_file_box':
        return {
          dialogFormType: 'PATH_INPUT',
          label: data.select_title,
          defaultPath: data.default_path,
          selectType: data.open_type,
          filter: data.file_type,
          isMultiple: data.multiple_choice,
          // defaultValue: data.open_type === 'folder' ? data.default_path : '',
        }
      case 'Dialog.message_box':
        return {
          dialogFormType: 'MESSAGE_CONTENT',
          messageType: data.message_type,
          messageContent: data.message_content,
          defaultValue: data?.default_button || data?.default_button_c || data?.default_button_cn || data?.default_button_y || data?.default_button_yn,
        }
      default:
        break
    }
  }
  const temp = getUserFormOption(data)
  return {
    mode: 'window',
    title: data.box_title || data.box_title_file || data.box_title_folder,
    buttonType: data?.button_type || 'confirm_cancel',
    itemList: [{
      bind: data.outputkey,
      ...temp,
    }],
    formModel: {
      [data.outputkey]: temp?.defaultValue || '',
    },
  }
}

async function resizeWindow(minWinHeight: number) {
  // 计算设置自定义对话框窗口高度，实现高度随动
  const { offsetWidth: bodyWidth } = document.body
  const userHeaderHeight = (document.querySelector('.userform-header') as HTMLElement)?.offsetHeight
  const userFooterHeight = (document.querySelector('.userform-footer') as HTMLElement)?.offsetHeight
  const formHeight = document.forms[0].offsetHeight
  // 判断计算高度是否超过了所在屏幕高度
  const screenWorkArea = await windowManager.getScreenWorkArea()
  const resHeight = clamp(formHeight + userHeaderHeight + userFooterHeight + 65, minWinHeight, screenWorkArea.height)
  console.log('resHeight', resHeight)
  await windowManager.setWindowSize({ width: bodyWidth, height: resHeight })
  windowManager.centerWindow()

  utilsManager.invoke('page_handler', {
    operType: 'UserForm',
    data: 'noresize',
  })
}

const targetInfo = new URL(location.href).searchParams
const windowOption = transformBasic(JSON.parse(targetInfo.get('option'))) as DialogOption
const replyBaseData = JSON.parse(targetInfo.get('reply')) ?? {}

onMounted(() => {
  // 调整弹窗高度
  const hasDatePicker = windowOption.itemList.some(item => ['DATEPICKER', 'RANGERPICKER'].includes(item.dialogFormType))
  const minWinHeight = hasDatePicker ? PICKER_MIN_HEIGHT : OTHER_MIN_HEIGHT
  resizeWindow(minWinHeight)
})

function handleClose() {
  windowManager.closeWindow(WINDOW_NAME.USERFORM)
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
  <UserFormDialog draggable :option="windowOption" @close="handleClose" @save="handleSave" />
</template>
