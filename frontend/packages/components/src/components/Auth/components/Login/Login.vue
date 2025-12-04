<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Tabs, TabPane } from 'ant-design-vue'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useLoginForm } from './hooks/useLoginForm'
import type { LoginMode, AsyncAction } from '../../interface'

const { running } = defineProps({
  running: { type: String as () => AsyncAction, default: 'IDLE' },
})

const emit = defineEmits<{
  submit: [data: any, mode: LoginMode]
  sendCaptcha: [phone: string]
  switchToRegister: []
  forgetPassword: []
}>()

const passwordLoading = computed(() => running === 'PASSWORD')
const codeLoading = computed(() => running === 'CODE')

const account = useLoginForm('PASSWORD', emit as any)
const phone   = useLoginForm('CODE', emit as any)

const currentMode = ref<LoginMode>('PASSWORD')

watch(() => currentMode.value, (_, old) => (old === 'PASSWORD' ? account : phone).clearValidates())

</script>

<template>
  <FormLayout
    :wrap-class="'auth-login h-full'"
  >
    <template #header>
      <div class="text-[24px] text-[#000000D9] mb-[24px] font-[600] text-center dark:text-[#FFFFFF] font-sans">欢迎使用星辰RPA</div>
    </template>
    <Tabs
      v-model:activeKey="currentMode"
      centered
      type="card"
      class="h-full"
    >
      <TabPane key="PASSWORD" tab="账号">        
        <DynamicForm
          :loading="passwordLoading"
          :ref="account.formRef"
          :config="account.config"
          v-model="account.formData"
          :handleEvents="account.handleEvents"
        />
      </TabPane>

      <TabPane key="CODE" tab="手机验证码">
        <DynamicForm
          :loading="codeLoading"
          :ref="phone.formRef"
          :config="phone.config"
          v-model="phone.formData"
          :handleEvents="phone.handleEvents"
        />
      </TabPane>
    </Tabs>
  </FormLayout>
</template>
