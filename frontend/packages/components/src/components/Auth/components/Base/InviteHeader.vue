<script setup lang="ts">
interface Props {
  type?: 'market' | 'enterprise'
  userName?: string
  targetName?: string
}

const { type = 'market', userName = '', targetName = '' } = defineProps<Props>()

</script>

<template>
  <div class="text-[14px] text-[#000000D9] mb-[24px] text-center dark:text-[#FFFFFF]">
    <div>{{ userName }} <span class="text text-[#00000073] dark:text-[#FFFFFF73] ml-[5px]">邀请您加入{{type === 'market' ? '应用市场' : '工作空间'}}</span></div>
    <div class="text-[20px] mt-[10px] font-[600]">{{ targetName }}</div>
  </div>
 </template>
