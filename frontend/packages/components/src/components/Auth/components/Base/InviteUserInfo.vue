<script setup lang="ts">
import { Button } from 'ant-design-vue'
import FormLayout from './FormLayout.vue'
import type { InviteInfo } from '../../interface'

interface Props {
  inviteInfo: InviteInfo
  currentUser?: { name?: string; phone?: string }
}

const { inviteInfo } = defineProps<Props>()
const { inviteType } = inviteInfo

const emit = defineEmits<{
  back: []
  join: []
  switchToLogin: []
}>()

</script>

<template>
  <FormLayout
    wrap-class="auth-invite-user-info"
    :invite-info="inviteInfo"
    :show-agreement="inviteType === 'enterprise'"
    :agreement-type="'show'"
  >
    <template v-if="inviteType === 'enterprise'">
      <div class="bg-[#F9FAFB] dark:bg-[#ffffff15] rounded-[8px] text-[14px] my-[20px] p-[16px] text-[#00000073] dark:text-[#FFFFFF73]">
        将以下面身份加入：
        <div class="my-[10px]">姓名：<span class="text-[#000000] dark:text-[#FFFFFF]">{{currentUser?.name }}</span></div>
        <div>手机号：<span class="text-[#000000] dark:text-[#FFFFFF]">{{currentUser?.phone }}</span></div>
      </div>
      <Button type="primary" size="large" class="absolute bottom-0" block @click="emit('join')">
        确认加入
      </Button>
    </template>
    <template v-else>
      <Button type="primary" size="large" class="" block @click="emit('join')">
        立即加入
      </Button>
      <div class="text-center text-[14px] border-t border-[#eeeeee] dark:border-[#ffffff15] mt-[20px] p-[16px] text-[#00000073] dark:text-[#FFFFFF73]">
        当前账号：{{currentUser?.name }}({{ currentUser?.phone }})
        <div class="text-[#726FFF] mt-[10px] cursor-pointer" @click="emit('switchToLogin')">使用其他账号</div>
      </div>
    </template>
  </FormLayout>
</template>
