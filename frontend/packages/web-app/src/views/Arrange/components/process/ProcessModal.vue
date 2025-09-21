<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { Form, message } from 'ant-design-vue'
import { computed, onBeforeMount, reactive } from 'vue'

import useProjectDocStore from '@/stores/useProjectDocStore'

const props = defineProps<{
  type: RPA.Flow.ProcessModuleType
  processItem?: RPA.Flow.ProcessModule
}>()

const modal = NiceModal.useModal()
const { addProcessOrModule, genProcessOrModuleName, renameProcessOrModule } = useProjectDocStore()

const categoryTitle = computed(() => props.type === 'process' ? '子流程' : 'Python模块')
const modalTitle = computed(() => props.processItem ? `编辑${categoryTitle.value}` : `新建${categoryTitle.value}`)
const nameTitle = computed(() => `${categoryTitle.value}名称`)

const formState = reactive({ name: '' })
const rulesRef = computed(() => ({
  name: [
    {
      required: true,
      message: `请输入${nameTitle.value}！`,
    },
  ],
}))

const { validate, validateInfos } = Form.useForm(formState, rulesRef)

onBeforeMount(async () => {
  if (props.processItem?.name) {
    formState.name = props.processItem.name
  }
  else {
    formState.name = await genProcessOrModuleName(props.type)
  }
})

async function handleOkConfirm() {
  await validate()

  const msgPrefix = props.processItem ? '更新' : '新建'

  try {
    if (props.processItem) {
      await renameProcessOrModule(props.type, formState.name, props.processItem.resourceId)
    }
    else {
      await addProcessOrModule(props.type, formState.name)
    }

    message.success(`${msgPrefix}成功`)
    modal.hide()
  }
  catch {
    message.error(`${msgPrefix}失败`)
  }
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="process-modal"
    :width="500"
    :title="modalTitle"
    @ok="handleOkConfirm"
  >
    <a-form layout="vertical">
      <div v-if="type === 'process'" class="mb-2.5">
        <span>{{ modalTitle }}：</span>
        <span>在流程具有较多操作步骤时，便于整体工程的管理。</span>
      </div>
      <a-form-item
        :label="nameTitle"
        name="name"
        v-bind="validateInfos.name"
      >
        <a-input v-model:value="formState.name" class="text-xs h-8 leading-none" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
