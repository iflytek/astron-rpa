<script setup lang="ts">
import { ref, watch } from 'vue'
import { Tabs, TabPane } from 'ant-design-vue'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useLoginForm } from './hooks/useLoginForm'
import type { LoginMode } from '../../interface'
import { loginProps } from '../../interface'

const props = defineProps(loginProps())
const emit = defineEmits<{
  submit: [data: any, mode: LoginMode]
  sendCaptcha: [phone: string]
  switchToRegister: []
  forgetPassword: []
}>()

const account = useLoginForm('account', emit as any)
const phone   = useLoginForm('phone', emit as any)

const currentMode = ref<LoginMode>('account')

watch(() => currentMode.value, (_, old) => (old === 'account' ? account : phone).resetForm())
</script>

<template>
  <FormLayout
    :wrap-class="'auth-login h-full'"
  >
    <template #header>
      <div class="text-[24px] text-[#000000D9] mb-[24px] font-[600] text-center dark:text-[#FFFFFF]">欢迎使用星辰RPA</div>
    </template>
    <Tabs
      v-model:activeKey="currentMode"
      centered
      type="card"
      class="h-full"
    >
      <TabPane key="account" tab="账号">
        <DynamicForm
          :ref="account.formRef"
          :config="account.config"
          v-model="account.formData"
          :emitEvent="account.emitEvent"
        />
      </TabPane>
  
      <TabPane key="phone" tab="手机验证码">
        <DynamicForm
          :ref="phone.formRef"
          :config="phone.config"
          v-model="phone.formData"
          :emitEvent="phone.emitEvent"
        />
      </TabPane>
    </Tabs>
  </FormLayout>
</template>
