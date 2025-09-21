<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { inject } from 'vue'

import { transDataForPreview } from '../utils/index'

import { UserFormDialogModal } from './index'

const emit = defineEmits(['saveData', 'close'])
const { dialogData } = inject('dialogData') as { dialogData: any }

function togglePreView() {
  const { title, buttonType } = dialogData.value
  const { itemList, formModel } = transDataForPreview(dialogData.value)
  NiceModal.show(UserFormDialogModal, {
    option: { mode: 'modal', title, buttonType, itemList, formModel },
  })
}

function handleOk() {
  // 只要有一个表单控件存在一个必填项，则required字段为true，后端需要
  const required = dialogData.value?.formList.some((item: any) => item?.required?.value)
  dialogData.value.table_required = required
  const saveData = dialogData.value?.formList.length
    ? JSON.stringify({
        value: dialogData.value,
        rpa: 'special',
      })
    : ''
  emit('saveData', saveData)
}
</script>

<template>
  <div class="dialog-modal_footer">
    <a-button type="primary" ghost @click="togglePreView">
      预览
    </a-button>
    <a-button @click="() => { emit('close') }">
      取消
    </a-button>
    <a-button type="primary" @click="handleOk">
      确定
    </a-button>
  </div>
</template>
