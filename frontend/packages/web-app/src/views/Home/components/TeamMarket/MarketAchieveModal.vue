<script setup lang="ts">
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { Input, message, Tooltip } from 'ant-design-vue'
import { h, reactive, ref } from 'vue'

import { getAppDetails, obtainApp } from '@/api/market'
import GlobalModal from '@/components/GlobalModal/index.ts'
import type { AnyObj } from '@/types/common'
import { SECURITY_RED } from '@/views/Home/components/TeamMarket/config/market.ts'

import type { cardAppItem } from '../../types/market'
import { usePermissionStore } from '@/stores/usePermissionStore'
import { ACTUATOR, DESIGNER } from '@/constants/menu'
interface FormState {
  marketId: string | number
  appId: string | number
  appName: string
  version: string
  obtainDirection: string[]
}

const props = defineProps<{
  record: cardAppItem
  versionLst: AnyObj
}>()

const emit = defineEmits(['refresh'])
const permissionStore = usePermissionStore()

const TYPE_ARR = [{
  label: '设计器',
  value: 'design',
  permission: DESIGNER,
  tip: '创建为一个新副本，可以编辑；源应用重新发版后不会收到更新',
}, {
  label: '执行器',
  value: 'execute',
  permission: ACTUATOR,
  tip: '可执行任务，不支持编辑；源应用重新发版后会收到更新',
}]

const modal = NiceModal.useModal()
const confirmLoading = ref(false)
const confirmAppName = ref('')

const formRef = ref<FormInstance>()
const formState = reactive<FormState>({
  marketId: props.record.marketId,
  appId: props.record.appId,
  appName: props.record.appName,
  version: props.versionLst[0]?.version,
  obtainDirection: [],
})

async function handleOk() {
  formRef.value.validate().then(() => {
    console.log(formState)
    confirmLoading.value = true
    obtainApp(formState).then(() => {
      confirmLoading.value = false
      const commonMsg = '获取成功'
      formState.obtainDirection.includes('design') && message.success(`${commonMsg}，已在设计器的我获取的列表中创建该应用的副本`)
      formState.obtainDirection.includes('execute') && message.success(`${commonMsg}，并自动启用该应用获取的版本`)
      emit('refresh')
      modal.hide()
    }).catch((err) => {
      confirmLoading.value = false
      const { code } = err
      if (![600001, '600001', 600000, '600000'].includes(code)) {
        message.error(err.message || err.msg)
        return
      }
      if ([600001, '600001'].includes(code)) {
        message.error('执行器中该应用当前版本已存在')
        return
      }
      if ([600000, '600000'].includes(code)) {
        const modal = GlobalModal.warning({
          title: '获取应用',
          content: () => {
            return h('div', [h('p', '设计器存在同名应用，请修改名称'), h('span', '名称：'), h(Input, { defaultValue: formState.appName, onChange: (e) => { confirmAppName.value = e.target.value; !confirmAppName.value && message.error('请输入名称') }, style: 'width: 120px' })])
          },
          onOk() {
            if (!confirmAppName.value) {
              message.error('请输入名称')
              return false
            }
            formState.appName = confirmAppName.value
            handleOk()
            modal.destroy()
          },
          maskClosable: true,
          centered: true,
          keyboard: false,
        })
      }
    })
  })
}

async function checkNumber() {
  if (formState.obtainDirection?.length === 0) {
    return Promise.reject(new Error('请至少选择一个获取类型！'))
  }
  return Promise.resolve()
}

// 设置下拉框默认选中版本为当前启用版本
async function setDefaultVersion() {
  getAppDetails({
    marketId: formState.marketId as string,
    appId: formState.appId as string,
  }).then(({ data }) => {
    const enableVersion = data?.versionInfoList.find(item => item.online === 1).versionNum
    formState.version = enableVersion
    console.log('enableVersion', enableVersion)
  })
}

setDefaultVersion()
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    title="获取"
    :confirm-loading="confirmLoading"
    centered
    @ok="handleOk"
  >
    <a-form ref="formRef" :model="formState" layout="vertical" autocomplete="off">
      <a-form-item label="获取版本">
        <a-select v-model:value="formState.version">
          <a-select-option v-for="version in props.versionLst" :key="version.version" :value="version.version">
            {{ `版本${version.version}` }}
          </a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item
        label="获取至"
        name="type"
        :rules="[{ validator: checkNumber, trigger: 'change' }]"
      >
        <a-checkbox-group v-model:value="formState.obtainDirection">
          <a-checkbox v-for="type in TYPE_ARR" class="leading-[32px]" :key="type.value" :value="type.value" :disabled="(props.record.securityLevel === SECURITY_RED && type.value === 'design') || !permissionStore.can(type.permission, 'all')">
            {{ type.label }}
            <Tooltip :title="type.tip">
              <QuestionCircleOutlined style="color: gray;" />
            </Tooltip>
          </a-checkbox>
        </a-checkbox-group>
        <div v-if="TYPE_ARR.find(item => !permissionStore.can(item.permission, 'all'))" class="text-[12px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)">
          当前账号暂不开放{{TYPE_ARR.find(item => !permissionStore.can(item.permission, 'all'))?.label}}功能
        </div>
      </a-form-item>
    </a-form>
  </a-modal>
</template>
