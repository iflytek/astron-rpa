<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { Drawer, message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { reactive, ref, useTemplateRef } from 'vue'

import { getComponentDetail, getComponentNextVersion, publishComponent } from '@/api/project'
import AvatarSelect from '@/components/Avatar/AvatarSelect.vue'
import { COMPONENT_DEFAULT_ICON } from '@/constants/avatar'

interface FormState {
  name: string
  introduction: string
  icon: string
  nextVersion: number
  updateLog: string
}

const props = defineProps({
  componentId: {
    type: String,
    required: true,
  },
})

const emits = defineEmits(['refresh'])

const modal = NiceModal.useModal()
const { t } = useTranslation()
const formRef = useTemplateRef<FormInstance>('formRef')

const loading = ref(false)
const formState = reactive<Partial<FormState>>({})

async function initForm() {
  const [detail, nextVersion] = await Promise.all([
    getComponentDetail({ componentId: props.componentId }),
    getComponentNextVersion({ componentId: props.componentId }),
  ])
  formState.name = detail.name
  formState.introduction = detail.introduction
  formState.icon = detail.icon || COMPONENT_DEFAULT_ICON
  formState.nextVersion = nextVersion
}

async function handleSubmit() {
  await formRef.value.validate()

  const success = await publishComponent({ ...formState, componentId: props.componentId })
  if (success) {
    message.success('发版成功')
    modal.hide()
    emits('refresh')
  }
}

initForm()
</script>

<template>
  <Drawer
    v-bind="NiceModal.antdDrawer(modal)"
    :title="t('components.publishComponent')"
    class="publish-modal"
    :width="568"
    :footer="null"
  >
    <template #extra>
      <a-space>
        <a-button @click="modal.hide">
          {{ t("cancel") }}
        </a-button>
        <a-button type="primary" @click="handleSubmit">
          {{ t("confirm") }}
        </a-button>
      </a-space>
    </template>

    <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
      <a-spin />
    </div>

    <a-form ref="formRef" :model="formState" layout="vertical" class="px-6 py-2">
      <a-form-item :label="t('components.avatar')" name="icon">
        <AvatarSelect v-model:value="formState.icon" />
      </a-form-item>
      <a-form-item :label="t('components.componentName')" name="name" required>
        <a-input v-model:value="formState.name" :placeholder="t('common.enter')" />
      </a-form-item>
      <a-form-item :label="t('components.componentDescription')" name="introduction">
        <a-textarea v-model:value="formState.introduction" :placeholder="t('common.enter')" :rows="3" />
      </a-form-item>

      <a-divider />

      <div class="flex items-center gap-1 mb-6 text-xs leading-[22px]">
        <span class="text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]">{{ t('currentVersion') }}：</span>
        <span>版本{{ formState.nextVersion }}</span>
      </div>

      <a-form-item :label="t('components.updateLog')" name="updateLog">
        <a-textarea v-model:value="formState.updateLog" :placeholder="t('common.enter')" :rows="3" />
      </a-form-item>
    </a-form>
  </Drawer>
</template>
