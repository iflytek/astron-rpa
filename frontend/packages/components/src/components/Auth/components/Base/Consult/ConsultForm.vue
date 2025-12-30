<script setup lang="ts">
import DynamicForm from '../DynamicForm.vue'
import { useConsultForm } from './hooks/useConsultForm.ts'
import type { RegisterMode, ConsultFormData } from '../../../interface.ts'

const { loading, consultEdition, consultType } = defineProps({
  loading: { 
    type: Boolean, 
    default: false 
  },
  consultEdition: {
    type: String as () => 'professional' | 'enterprise' | '',
    default: ''
  },
  consultType: {
    type: String as () => 'consult' | 'renewal',
    default: 'consult'
  }
})

const emit = defineEmits<{
  submit: [data: ConsultFormData, mode: RegisterMode]
}>()

const { config, formRef, formData, handleEvents, resetForm } = useConsultForm({ consultEdition, consultType }, emit as any)

defineExpose({
  resetForm
})
</script>

<template>
  <DynamicForm
    class="auth-consult-form"
    v-if="config"
    :loading="loading"
    ref="formRef"
    :config="config"
    v-model="formData"
    :handleEvents="handleEvents"
  />
</template>