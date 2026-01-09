<script setup lang="ts">
import { Button } from 'ant-design-vue'

import type { InviteInfo } from '../../interface'

import FormLayout from './FormLayout.vue'

interface Props {
  inviteInfo: InviteInfo
  currentUser?: { name?: string, phone?: string }
}

const { inviteInfo } = defineProps<Props>()
const emit = defineEmits<{
  back: []
  join: []
  switchToLogin: []
}>()

const { inviteType } = inviteInfo
</script>

<template>
  <FormLayout
    wrap-class="auth-invite-user-info"
    :invite-info="inviteInfo"
    :show-agreement="inviteType === 'enterprise'"
    agreement-type="show"
  >
    <div class="relative h-full pt-[20px]">
      <div class="w-full bg-[#F9FAFB] dark:bg-[#ffffff15] rounded-[8px] text-[14px] p-[16px] text-[#00000073] dark:text-[#FFFFFF73] ">
        当前账号：
        <div class="my-[10px]">
          姓名：<span class="text-[#000000] dark:text-[#FFFFFF]">{{ currentUser?.name }}</span>
        </div>
        <div>手机号：<span class="text-[#000000] dark:text-[#FFFFFF]">{{ currentUser?.phone }}</span></div>
      </div>
      <div class="w-full absolute bottom-0">
        <Button type="primary" size="large" block @click="emit('join')">
          确认加入
        </Button>
        <div class="text-[#726FFF] mt-[10px] text-center text-[12px] cursor-pointer" @click="emit('switchToLogin')">
          使用其他账号
        </div>
      </div>
    </div>
  </FormLayout>
</template>
