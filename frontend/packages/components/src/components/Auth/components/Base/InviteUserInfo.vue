<script setup lang="ts">
import InviteFormLayout from './InviteFormLayout.vue'

interface Props {
  type?: 'market' | 'enterprise'
  userName?: string
  targetName?: string
  currentUser?: { name?: string; phone?: string }
}

const { type, userName, targetName } = withDefaults(defineProps<Props>(), {
  type: 'market',
  userName: '',
  targetName: '',
})

const emit = defineEmits<{
  back: []
  joinEnterprise: []
  joinMarket: []
  switchToLogin: []
}>()


</script>

<template>
  <InviteFormLayout
    :show-back="type === 'enterprise'"
    @back="() => emit('back')"
    :type="type" 
    :loginName="userName" 
    :target-name="targetName"
    :show-agreement="type === 'enterprise'"
  >
  <template v-if="type === 'enterprise'">
    <div class="bg-[#F9FAFB] dark:bg-[#ffffff15] rounded-[8px] text-[14px] my-[20px] p-[16px] text-[#00000073] dark:text-[#FFFFFF73]">
      将以下面身份加入：
      <div>姓名：<span class="text-[#000000] dark:text-[#FFFFFF]">{{currentUser?.name }}</span></div>
      <div>手机号：<span class="text-[#000000] dark:text-[#FFFFFF]">{{currentUser?.phone }}</span></div>
    </div>
    <Button type="primary" class="" block @click="emit('joinEnterprise')">
      确认加入
    </Button>
    </template>
    <template v-else>
      <Button type="primary" class="" block @click="emit('joinMarket')">
        立即加入
      </Button>
      <div class="text-center text-[14px] border-t border-[#eeeeee] dark:border-[#ffffff15] mt-[20px] p-[16px] text-[#00000073] dark:text-[#FFFFFF73]">
        当前账号：{{currentUser?.name }}({{ currentUser?.phone }})
        <div class="text-[#726FFF] mt-[10px] cursor-pointer" @click="emit('switchToLogin')">使用其他账号</div>
      </div>
    </template>
  </InviteFormLayout>
</template>
