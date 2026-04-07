<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { Form, message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, onBeforeMount, reactive } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

const props = defineProps<{
  type: RPA.Process.ProcessModuleType
  processItem?: RPA.Process.ProcessModule
}>()

const modal = NiceModal.useModal()

const processStore = useProcessStore()
const { t } = useTranslation()

const categoryTitle = computed(() => props.type === 'process' ? t('processModal.subProcess') : t('processModal.pythonModule'))
const modalTitle = computed(() => t('processModal.title', { action: props.processItem ? t('edit') : t('new'), category: categoryTitle.value }))
const nameTitle = computed(() => t('processModal.nameTitle', { category: categoryTitle.value }))

const formState = reactive({ name: '' })
const rulesRef = computed(() => ({
  name: [
    {
      required: true,
      message: t('processModal.enterName', { name: nameTitle.value }),
    },
    {
      validator: (_rule: any, value: string) => {
        const exists = processStore.canvasManager.processList.some(
          p => p.state.name === value && p.state.resourceId !== props.processItem?.resourceId
        )
        if (exists) {
          return Promise.reject(`${nameTitle.value}已存在`)
        }
        return Promise.resolve()
      },
    },
  ],
}))

const { validate, validateInfos } = Form.useForm(formState, rulesRef)

onBeforeMount(async () => {
  if (props.processItem?.resourceId) {
    const tab = processStore.canvasManager.getTab(props.processItem.resourceId)
    formState.name = tab?.state.name || props.processItem.name
  }
  else {
    formState.name = await processStore.canvasManager.genTabName(props.type)
  }
})

async function handleOkConfirm() {
  await validate()

  const msgPrefix = props.processItem ? t('common.update') : t('create')

  try {
    if (props.processItem) {
      await processStore.canvasManager.renameTab(props.processItem.resourceId, formState.name)
    }
    else {
      await processStore.canvasManager.createTab(props.type, formState.name)
    }

    message.success(t('processModal.actionSuccess', { action: msgPrefix }))
    modal.hide()
  }
  catch {
    message.error(t('processModal.actionFail', { action: msgPrefix }))
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
        <span>{{ $t('processModal.tip') }}</span>
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
