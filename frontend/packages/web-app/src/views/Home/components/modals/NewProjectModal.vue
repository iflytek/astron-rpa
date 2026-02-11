<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { watchImmediate } from '@vueuse/core'
import type { FormInstance } from 'ant-design-vue'
import type { RuleObject } from 'ant-design-vue/es/form'
import { useTranslation } from 'i18next-vue'
import { isFunction } from 'lodash-es'
import { reactive, ref } from 'vue'

interface FormState {
  name: string
}

const props = defineProps<{
  title?: string
  name?: string
  defaultName?: string | (() => Promise<string>)
  rules?: RuleObject[]
  onConfirm: (name: string) => Promise<void>
}>()

const modal = NiceModal.useModal()
const { t } = useTranslation()

const loading = ref(false)
const formRef = ref<FormInstance>()
const formState = reactive<FormState>({ name: '' })

async function handleOk() {
  const valid = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    await props.onConfirm(formState.name)
  }
  finally {
    loading.value = false
  }
}

watchImmediate(
  () => props.defaultName,
  async (newVal) => {
    if (newVal) {
      formState.name = isFunction(newVal) ? await newVal() : newVal
    }
  },
)
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :width="400"
    :title="title"
    :confirm-loading="loading"
    @ok="handleOk"
  >
    <a-form
      ref="formRef"
      :model="formState"
      autocomplete="off"
      layout="vertical"
    >
      <a-form-item
        :label="name"
        name="name"
        :rules="[
          { required: true, message: t('common.enterPlaceholder', { name }) },
          ...(props.rules || []),
        ]"
      >
        <a-input v-model:value="formState.name" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
