<script setup lang="ts">
import DynamicForm from '../Base/DynamicForm.vue'
import InviteFormLayout from '../Base/InviteFormLayout.vue'

import { useFillUserInfo } from './hooks/useFillUserInfo'
import type { 
  EnterpriseInvitFormData
} from '../../interface'

const props = defineProps<{ inviteInfo: any, currentUser: any }>()
const emit = defineEmits<{
  submit: [data: EnterpriseInvitFormData]
  back: []
}>()

const { formRef, formData, config, emitEvent } = useFillUserInfo(emit as any)
</script>

<template>
  <InviteFormLayout
    :wrap-class="'auth-invite h-full'"
    :show-back="true"
    @back="() => emit('back')"
    :type="'enterprise'"
    :user-name="props.inviteInfo?.userName"
    :target-name="props.inviteInfo?.enterpriseName"
    :show-agreement="true"
  >
    <div class="text-[12px] text-[#00000073] dark:text-[#FFFFFF73]">请完善以下信息</div>
    <DynamicForm
      ref="formRef"
      :config="config"
      v-model="formData"
      :emitEvent="emitEvent"
      class="auth-set-password-form my-[12px]"
    />
  </InviteFormLayout>
</template>