<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { Form, message, Select, Switch } from 'ant-design-vue'
import { reactive, ref } from 'vue'

import { shareComponentToMarket } from '@/api/robot'
import Avatar from '@/components/Avatar/Avatar.vue'
import type { AnyObj } from '@/types/common'

const props = defineProps<{
  record: AnyObj
  marketList: Array<AnyObj>
}>()

const emits = defineEmits(['refresh'])

interface FormState {
  componentId: string
  componentName: string
  version: number
  marketIdList: Array<string>
  editFlag: boolean | number
}

const modal = NiceModal.useModal()

const formRef = ref<FormInstance>()
const formState = reactive<FormState>({
  componentId: props.record.componentId,
  componentName: props.record.componentName,
  version: props.record.version,
  marketIdList: [],
  editFlag: true,
})

const confirmLoading = ref(false)

function shareToMarket() {
  shareComponentToMarket({
    componentId: formState.componentId,
    componentName: formState.componentName,
    version: formState.version,
    marketIdList: formState.marketIdList,
    // editFlag: formState.editFlag ? 1 : 0,
  }).then(() => {
    confirmLoading.value = false
    message.success('分享成功')
    emits('refresh')
    modal.hide()
  }).catch(() => {
    confirmLoading.value = false
  }).finally(() => {
    confirmLoading.value = false
  })
}

function handleOk() {
  formRef.value.validate().then(() => {
    confirmLoading.value = true
    shareToMarket()
  })
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    title="分享组件"
    :confirm-loading="confirmLoading"
    @ok="handleOk"
  >
    <div class="header">
      <Avatar :robot-name="formState.componentName" :icon="props.record.icon" size="large" />
      <div>{{ formState.componentName }}</div>
    </div>
    <Form ref="formRef" label-align="left" :model="formState" :label-col="{ span: 5 }" :wrapper-col="{ span: 16 }" autocomplete="off">
      <Form.Item label="分享至市场" name="marketIdList" :rules="[{ required: true, message: '请选择市场' }]">
        <Select v-model:value="formState.marketIdList" mode="multiple" :options="marketList" :field-names="{ label: 'marketName', value: 'marketId' }" allow-clear />
      </Form.Item>
      <!-- <Form.Item label="开放源码">
        <Switch v-model:checked="formState.editFlag" />
      </Form.Item> -->
    </Form>
  </a-modal>
</template>

<style lang="scss" scoped>
.header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 8px;
  padding-bottom: 10px;
  div {
    font-size: 16px;
    font-weight: 600;
  }
}
</style>
