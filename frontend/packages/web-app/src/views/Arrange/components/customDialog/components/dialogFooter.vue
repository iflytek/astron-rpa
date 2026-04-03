<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { isEmpty } from 'lodash-es'
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
  const formList = dialogData.value?.formList
  // 只要有一个表单控件存在一个必填项，则required字段为true，后端需要
  const required = formList.some((item: any) => item?.required?.value)
  dialogData.value.table_required = required
  const saveData = isEmpty(formList) ? '' : JSON.stringify(dialogData.value)
  emit('saveData', saveData)
}
</script>

<template>
  <div class="dialog-modal_footer">
    <a-button type="primary" ghost @click="togglePreView">
      {{ $t('preview') }}
    </a-button>
    <a-button @click="() => emit('close')">
      {{ $t('cancel') }}
    </a-button>
    <a-button type="primary" @click="handleOk">
      {{ $t('confirm') }}
    </a-button>
  </div>
</template>
