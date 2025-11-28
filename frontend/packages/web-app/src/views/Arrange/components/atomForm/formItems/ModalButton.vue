<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { validateContractResult } from '@/api/contract'
import to from 'await-to-js'
import { reduce } from 'lodash-es'

import { useProcessStore } from '@/stores/useProcessStore'
import { CustomDialog } from '@/views/Arrange/components/customDialog'
import { UserFormDialogModal } from '@/views/Arrange/components/customDialog/components'
import { ContractValidateModal, EmailTextReplaceModal, TextareaModal } from '@/views/Arrange/components/tools/components'
import { GLOBAL_VAR_TYPE, ORIGIN_VAR, PARAMETER_VAR_TYPE, PROCESS_VAR_TYPE } from '@/views/Arrange/config/atom'

import type { FormItemProps, FormItemEmits } from './index'
import { getRealValue, getUserFormOption } from '../hooks/usePreview'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const { canvasManager } = useProcessStore()
const loading = ref(false)

const updateValue = (value: any) => {
  emits('update', props.item.key, value)
}

const handleClick = async () => {
  console.log('点击了ModalButton按钮', props.item)

  if (props.item.key === 'design_interface') {
    const boxTitleValue = props.values['box_title']
    const title = getRealValue(boxTitleValue)

    NiceModal.show(CustomDialog, {
      title,
      option: props.item.value as string,
      onOk: updateValue
    })
  }
  else if (props.item.key === 'preview_button') {
    const { key } = canvasManager.activeTab.nodeParameter.activeAtom;
    const formOptions = getUserFormOption(key, props.values);
    NiceModal.show(UserFormDialogModal, {
      option: { mode: 'modal', buttonType: 'confirm_cancel', ...formOptions },
    })
  }
  else if (props.item.key === 'contract_validate') {
    const targetValue = props.values['custom_factors']
    // 前置判断是否有要素
    if (!targetValue) {
      message.warning('请先添加要素')
      return
    }

    // 是否有流程变量
    let hasProcessVarType = false

    const params = reduce(props.values, (result, value, key) => {
      const realValue = getRealValue(value, PROCESS_VAR_TYPE)
      result[key] = realValue

      if (realValue.includes(PROCESS_VAR_TYPE)) {
        hasProcessVarType = true
      }

      return result
    }, {})

    if (hasProcessVarType) {
      message.warning('存在流变量无法验证效果')
      return
    }

    loading.value = true
    const [err, res] = await to(validateContractResult(params))
    if (!err) {
      NiceModal.show(ContractValidateModal, { dataList: res.data })
    }
    loading.value = false
  }
  else if (props.item.key === 'replace_table') {
    NiceModal.show(EmailTextReplaceModal, {
      option: props.item.value as string,
      onOk: updateValue
    })
  }
}
</script>

<template>
  <a-button type="primary" block :loading="loading" :disabled="loading" @click="handleClick">
    {{ props.item.title }}
  </a-button>
</template>
