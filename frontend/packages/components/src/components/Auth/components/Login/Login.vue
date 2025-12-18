<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Tabs, TabPane } from 'ant-design-vue'
import FormLayout from '../Base/FormLayout.vue'
import DynamicForm from '../Base/DynamicForm.vue'
import { useLoginForm } from './hooks/useLoginForm'
import type { LoginMode, AsyncAction, InviteInfo } from '../../interface'

const { running, inviteInfo } = defineProps({
  running: { 
    type: String as () => AsyncAction, 
    default: 'IDLE' 
  },
  inviteInfo: { 
    type: Object as () => InviteInfo, 
    default: () => null 
  },
})

const emit = defineEmits<{
  submit: [data: any, mode: LoginMode]
  switchToRegister: []
  forgetPassword: []
}>()

const sharedAgreement = ref(false)

const passwordLoading = computed(() => running === 'PASSWORD')
const codeLoading = computed(() => running === 'CODE')

const account = useLoginForm('PASSWORD', inviteInfo, emit as any)
const phone = useLoginForm('CODE', inviteInfo, emit as any)

account.formData.agreement = sharedAgreement.value
phone.formData.agreement = sharedAgreement.value

const currentMode = ref<LoginMode>('PASSWORD')

watch(() => currentMode.value, (_, old) => (old === 'PASSWORD' ? account : phone).clearValidates())

watch(() => account.formData.agreement, (v) => {
  sharedAgreement.value = v || false
  phone.formData.agreement = v || false
})

watch(() => phone.formData.agreement, (v) => {
  sharedAgreement.value = v || false
  account.formData.agreement = v || false
})

</script>

<template>
  <FormLayout
    :wrap-class="'auth-login h-full'"
    :invite-info="inviteInfo"
  >
    <template v-if="!inviteInfo" #header>
      <div class="text-[24px] text-[#000000D9] mb-[8px] font-[600] text-center dark:text-[#FFFFFF] font-sans">欢迎使用星辰RPA</div>
      <div class="text-[12px] text-[#000000A6] mb-[24px] text-center dark:text-[#FFFFFF] font-sans">使用您的讯飞账号</div>
    </template>
    <Tabs
      v-model:activeKey="currentMode"
      centered
      type="card"
      class="h-full"
    >
      <TabPane key="PASSWORD" tab="密码登录">        
        <DynamicForm
          :loading="passwordLoading"
          :ref="account.formRef"
          :config="account.config"
          v-model="account.formData"
          :handleEvents="account.handleEvents"
        />
      </TabPane>

      <TabPane key="CODE" tab="验证码登录">
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
