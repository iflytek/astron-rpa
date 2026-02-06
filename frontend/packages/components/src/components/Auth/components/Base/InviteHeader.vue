<script setup lang="ts">
import type { InviteInfo } from '../../interface'

const { inviteInfo } = defineProps<{
  inviteInfo: InviteInfo
}>()
</script>

<template>
  <div class="text-[20px] md:text-[14px] mb-[24px] text-center text-[#000000D9] dark:text-[#FFFFFF]">
    <div>{{ inviteInfo.inviterName }} <span class="text ml-[5px]">邀请您加入{{ inviteInfo.inviteType === 'market' ? '应用市场' : '工作空间' }}</span></div>
    <div class="text-[32px] md:text-[20px] mt-[10px] font-[600]">
      {{ inviteInfo.inviteType === 'market' ? inviteInfo.marketName : inviteInfo.deptName }}
    </div>
  </div>
</template>
