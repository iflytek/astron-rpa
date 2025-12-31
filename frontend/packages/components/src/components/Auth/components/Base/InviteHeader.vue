<script setup lang="ts">
import type { InviteInfo } from '../../interface'

const { inviteInfo } = defineProps<{
  inviteInfo: InviteInfo
}>()
</script>

<template>
  <div class="text-[14px] text-[#000000D9] mb-[24px] text-center dark:text-[#FFFFFF]">
    <div>{{ inviteInfo.inviterName }} <span class="text text-[#00000073] dark:text-[#FFFFFF73] ml-[5px]">邀请您加入{{ inviteInfo.inviteType === 'market' ? '应用市场' : '工作空间' }}</span></div>
    <div class="text-[20px] mt-[10px] font-[600]">
      {{ inviteInfo.inviteType === 'market' ? inviteInfo.marketName : inviteInfo.enterpriseName }}
    </div>
  </div>
</template>
