<script setup lang="ts">
import { message, Modal } from 'ant-design-vue'
import { computed, ref } from 'vue'

import { submitConsult, submitRenewal } from '../../../api/login.ts'
import type { ConsultFormData } from '../../../interface.ts'
import FormLayout from '../FormLayout.vue'

import ConsultForm from './ConsultForm.vue'

const { consultTitle, consultEdition, consultType } = defineProps<{
  consultTitle?: string
  consultEdition?: 'professional' | 'enterprise'
  consultType?: 'consult' | 'renewal'
}>()

const formType = computed(() => {
  return consultEdition === 'professional' ? 1 : 2
})

const visible = ref(false)

function showModal() {
  visible.value = true
}
function closeModal() {
  visible.value = false
}

const loading = ref(false)
async function submit(data: ConsultFormData) {
  loading.value = true
  const fn = consultType === 'renewal' ? submitRenewal : submitConsult
  const params = { ...data }
  if (consultType === 'renewal') {
    params.formType = formType.value
  }
  await fn(params)
  message.success('提交成功')
  loading.value = false
  closeModal()
}

defineExpose({
  showModal,
  closeModal,
})
</script>

<template>
  <Modal
    :open="visible"
    centered
    class="tenant-modal"
    :width="400"
    :z-index="1099"
    :footer="null"
    @cancel="closeModal"
  >
    <FormLayout wrap-class="auth-consult w-full !h-[460px] relative !px-[16px] !py-[20px] !bg-[transparent]" content-class="!h-[calc(100%-52px)]" :show-back="false">
      <template #header>
        <div class="text-[18px] text-[#000000D9] mb-[24px] font-[600] text-center dark:text-[#FFFFFF]">
          {{ consultTitle || (consultType === 'renewal' ? '续费' : '咨询') }}
        </div>
      </template>
      <ConsultForm
        v-if="visible"
        :consult-edition="consultEdition"
        :consult-type="consultType"
        @submit="submit"
      />
    </FormLayout>
  </Modal>
</template>
