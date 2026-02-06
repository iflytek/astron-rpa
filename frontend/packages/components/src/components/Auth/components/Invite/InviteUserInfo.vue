<script setup lang="ts">
import type { InviteInfo } from '../../interface'
import DynamicForm from '../Base/DynamicForm.vue'
import FormLayout from '../Base/FormLayout.vue'

import { useInviteUserInfo } from './hooks/useInviteUserInfo'

const { currentUser, inviteInfo } = defineProps({
  currentUser: {
    type: Object as () => { name?: string, phone?: string },
    default: () => ({}),
  },
  inviteInfo: {
    type: Object as () => InviteInfo,
    default: () => null,
  },
})
const emit = defineEmits<{
  submit: []
  switchToLogin: []
}>()

const { formRef, formData, config, handleEvents } = useInviteUserInfo(currentUser, emit as any)
</script>

<template>
  <FormLayout
    wrap-class="auth-invite-user-info bg-[#ffffff]
    w-full !h-[480px] fixed left-0 bottom-0 rounded-t-[24px] z-[999]
    md:w-[400px] md:!h-[540px] md:static md:rounded-[16px]"
    :invite-info="inviteInfo"
  >
    <div class="w-full rounded-[8px] text-[14px] mb-[12px] text-[#000000A6] dark:text-[#FFFFFF73] ">
      当前账号
    </div>
    <DynamicForm
      ref="formRef"
      v-model="formData"
      :config="config"
      :handle-events="handleEvents"
      class="auth-invite-user-form"
    />
  </FormLayout>
</template>
