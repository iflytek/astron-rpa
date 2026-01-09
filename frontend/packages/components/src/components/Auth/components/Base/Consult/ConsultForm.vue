<script setup lang="ts">
import type { ConsultFormData, RegisterMode } from '../../../interface.ts'
import DynamicForm from '../DynamicForm.vue'

import { useConsultForm } from './hooks/useConsultForm.ts'

const { loading, consultEdition, consultType } = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  consultEdition: {
    type: String as () => 'professional' | 'enterprise' | '',
    default: '',
  },
  consultType: {
    type: String as () => 'consult' | 'renewal',
    default: 'consult',
  },
})

const emit = defineEmits<{
  submit: [data: ConsultFormData, mode: RegisterMode]
}>()

const { config, formRef, formData, handleEvents, resetForm } = useConsultForm({ consultEdition, consultType }, emit as any)

defineExpose({
  resetForm,
})
</script>

<template>
  <DynamicForm
    v-if="config"
    ref="formRef"
    v-model="formData"
    class="auth-consult-form"
    :loading="loading"
    :config="config"
    :handle-events="handleEvents"
  />
</template>
