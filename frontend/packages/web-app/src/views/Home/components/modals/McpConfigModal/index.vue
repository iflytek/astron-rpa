<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { Input, message } from 'ant-design-vue'
import { isEmpty } from 'lodash-es'
import { ref } from 'vue'
import type { VxeGridProps } from 'vxe-table'

import VxeGrid from '@/plugins/VxeTable'

import { getConfigParams } from '@/api/atom'
import { getRobotEnglishName, getRobotLastIsExternalCall, setRobotIsExternalCall } from '@/api/robot'
import GlobalModal from '@/components/GlobalModal/index.vue'
import type { FormRules } from '@/types/common'

interface FormState {
  project_id: string
  name: string
  english_name: string
  description: string
  version: string | number
  status: boolean
  parameters: RPA.ConfigParamData[]
}

const props = defineProps<{ record: any }>()

const modal = NiceModal.useModal()
const confirmLoading = ref(false)

const formRef = ref<FormInstance>()
const formState = ref<FormState>({
  project_id: props.record.robotId,
  name: '',
  english_name: '',
  description: '',
  version: `${props.record.version}`,
  status: false,
  parameters: [],
})
const rules: FormRules = {
  name: [
    { required: true, message: '请输入应用名称', trigger: 'change' },
  ],
  english_name: [
    { required: true, message: '请输入应用英文名称', trigger: 'change' },
  ],
  description: [
    { required: true, message: '请输入应用简介', trigger: 'change' },
  ],
}

const DIRRCTION_MAP = {
  0: '输入',
  1: '输出',
}
const gridOptions: VxeGridProps<RPA.ConfigParamData> = {
  size: 'mini',
  scrollY: { enabled: true },
  border: true,
  showOverflow: true,
  // keepSource: true,
  rowConfig: {
    isHover: true,
    keyField: 'project_id', // 指定使用 id 字段作为行键
  },
  columns: [
    { field: 'varName', title: '变量名' },
    { field: 'varDirection', title: '输入/输出', slots: { default: 'usage_default' } },
    { field: 'varType', title: '类型' },
    { field: 'varDescribe', title: '简介', slots: { default: 'desc_default' } },
  ],
}

function handleAutoTranslate() {
  getRobotEnglishName(formState.value.name).then((res) => {
    formState.value.english_name = res.data || ''
  })
}
function initData() {
  Promise.all([
    getRobotLastIsExternalCall(props.record.robotId),
    getConfigParams({ robotId: props.record.robotId }),
  ]).then((res) => {
    const [mcpConfig, configParams] = res
    console.log('mcpConfig', JSON.stringify(mcpConfig))
    console.log('configParams', JSON.stringify(configParams))
    if (mcpConfig && !isEmpty(mcpConfig)) {
      // 只保留formState已有的字段
      const allowedKeys = Object.keys(formState.value)
      const filteredMcpConfig = Object.keys(mcpConfig)
        .filter(key => allowedKeys.includes(key))
        .reduce((obj, key) => {
          obj[key] = mcpConfig[key]
          return obj
        }, {} as Partial<FormState>)
      formState.value = {
        ...formState.value,
        ...filteredMcpConfig,
        status: mcpConfig.status === 1,
      }
    }
    // 比较parameters 和 configParams
    if (mcpConfig?.parameters?.length !== configParams.length) {
      formState.value.parameters = configParams
      console.log('formState starteeeee', formState.value)
      return
    }
    // 在数量相同的情况下，一旦发现有不同的id，则以设计器中的配置参数为准
    const mcpIds = mcpConfig.parameters.map(item => item.id)
    const configIds = configParams.map(item => item.id)
    const idsEqual = mcpIds.every((id, idx) => id === configIds[idx])
    formState.value.parameters = !idsEqual ? configParams : mcpConfig.parameters
    formState.value.version = props.record.version
    // console.log('idsEqual', idsEqual)
    console.log('formState startrrrrrr', formState.value)
  })
}
initData()

async function handleOk() {
  try {
    await formRef.value.validate()

    formState.value.parameters?.forEach((item) => {
      if (!item.varDescribe) {
        throw new Error('简介不能为空')
      }
    })

    await setRobotIsExternalCall({
      ...formState.value,
      project_id: props.record.robotId,
      status: formState.value.status ? 1 : 0,
      parameters: JSON.stringify(formState.value.parameters),
    })

    modal.hide()
  }
  catch {
    message.warning('请检查填写内容')
  }
}

function handleChange(varDescribe: string) {
  if (!varDescribe) {
    message.warning('简介不能为空')
  }
}
</script>

<template>
  <GlobalModal v-bind="NiceModal.antdModal(modal)" title="MCP配置" :confirm-loading="confirmLoading" @ok="handleOk">
    <a-form
      ref="formRef" layout="vertical" :rules="formState.status ? rules : null" :model="formState"
      autocomplete="off"
    >
      <a-form-item label="是否启用外部调用">
        <a-switch v-model:checked="formState.status" />
      </a-form-item>
      <template v-if="formState.status">
        <a-form-item label="应用名称" name="name">
          <a-input v-model:value="formState.name" />
        </a-form-item>
        <a-form-item label="应用英文名" name="english_name">
          <div class="flex items-center justify-between">
            <a-input v-model:value="formState.english_name" />
            <a-button size="small" class="ml-2" type="link" @click="handleAutoTranslate">
              点击翻译
            </a-button>
          </div>
        </a-form-item>
        <a-form-item label="应用简介" name="description">
          <a-textarea v-model:value="formState.description" :rows="4" />
        </a-form-item>
        <a-form-item label="应用参数">
          <VxeGrid
            v-bind="gridOptions" :data="formState.parameters" class="params-table w-full overflow-hidden"
            border="none" :height="100"
          >
            <template #usage_default="{ row }">
              <span>{{ DIRRCTION_MAP[row.varDirection] }}</span>
            </template>
            <template #desc_default="{ row }">
              <Input
                v-model:value="row.varDescribe" :bordered="false" class="text-xs text-inherit"
                @change="handleChange(row.varDescribe)"
              />
            </template>
          </VxeGrid>
        </a-form-item>
      </template>
    </a-form>
  </GlobalModal>
</template>

<style lang="scss" scoped>
:deep(.ant-form-item) {
  margin-bottom: 12px;
}
</style>
