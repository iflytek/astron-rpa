<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { Form, message, Select, Switch } from 'ant-design-vue'
import { reactive, ref } from 'vue'

import { getAllClassification, releaseApplication } from '@/api/market'
import { shareRobotToMarket } from '@/api/project'
import Avatar from '@/components/Avatar/Avatar.vue'
import type { AnyObj } from '@/types/common'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate'

const props = defineProps<{
  record: AnyObj
  marketList: Array<AnyObj>
}>()

const emits = defineEmits(['refresh'])

interface FormState {
  robotId: string
  appName: string
  category: string
  marketIdList: Array<string>
  editFlag: boolean | number
  version?: string
}

const modal = NiceModal.useModal()
const { applicationReleaseCheck } = useCommonOperate()
const categoryOptions = ref([])

const formRef = ref<FormInstance>()
const formState = reactive<FormState>({
  robotId: props.record.robotId,
  appName: props.record.robotName,
  category: undefined,
  marketIdList: [],
  editFlag: true,
})

const confirmLoading = ref(false)

function applicationShareToMarket() {
  releaseApplication({
    robotId: props.record.robotId,
    appName: props.record.robotName,
    robotVersion: props.record.version,
    marketIdList: formState.marketIdList,
    category: formState.category,
    editFlag: formState.editFlag ? 1 : 0,
  }).then(() => {
    confirmLoading.value = false
    message.success('已发起申请流程，请至应用市场关注后续申请结果。')
    emits('refresh')
    modal.hide()
  }).catch(() => {
    confirmLoading.value = false
  })
}

function shareToMarket() {
  shareRobotToMarket({
    ...formState,
    editFlag: formState.editFlag ? 1 : 0,
  }).then(() => {
    confirmLoading.value = false
    message.success('分享成功')
    emits('refresh')
    modal.hide()
  }).finally(() => {
    confirmLoading.value = false
  })
}

function handleOk() {
  formRef.value.validate().then(() => {
    confirmLoading.value = true
    applicationReleaseCheck({
      robotId: props.record.robotId,
      version: props.record.version,
    }, applicationShareToMarket, shareToMarket, () => {
      confirmLoading.value = false
    })
  })
}

getAllClassification().then((res) => {
  categoryOptions.value = res.data
  formState.category = categoryOptions.value[0]?.id || ''
})
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    title="分享应用"
    :confirm-loading="confirmLoading"
    @ok="handleOk"
  >
    <div class="header">
      <Avatar :robot-name="props.record.robotName" :icon="props.record.icon" :color="props.record.color" size="large" />
      <div>{{ props.record.robotName }}</div>
    </div>
    <Form ref="formRef" label-align="left" :model="formState" :label-col="{ span: 5 }" :wrapper-col="{ span: 16 }" autocomplete="off">
      <Form.Item label="应用类型">
        <Select
          v-model:value="formState.category"
          :field-names="{
            label: 'name',
            value: 'id',
          }"
          :options="categoryOptions"
        />
      </Form.Item>
      <Form.Item label="分享至市场" name="marketIdList" :rules="[{ required: true, message: '请选择市场' }]">
        <Select v-model:value="formState.marketIdList" mode="multiple" :options="marketList" :field-names="{ label: 'marketName', value: 'marketId' }" allow-clear />
      </Form.Item>
      <Form.Item label="开放源码">
        <Switch v-model:checked="formState.editFlag" />
      </Form.Item>
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
