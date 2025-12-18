<script setup lang="ts">
import Login from '../Login/Index.vue'
import StatusCard from '../Base/StatusCard.vue'
import InviteUserInfo from '../Base/InviteUserInfo.vue'
import { useInviteFlow } from './hooks/useInviteFlow'

const { baseUrl } = defineProps({
  baseUrl: { type: String },
})

const emit = defineEmits<{
  joinSuccess: [marketId: string]
}>()

const {
  currentStatus,
  inviteInfo,
  currentUser,
  switchToLogin,
  toJoin,
  openApp,
} = useInviteFlow(emit)
</script>

<template>
  <div class="auth-container-content invite-container h-[540px]">
    <StatusCard v-if="currentStatus === 'linkExpired'"
      :status="currentStatus"
      :title="'邀请链接已失效'"
      :desc="`请联系管理员获得新的链接`"
     />
    <Login v-else-if="currentStatus === 'needLogin'" :base-url="baseUrl" :invite-info="inviteInfo" @finish="toJoin" />
    <InviteUserInfo v-else-if="currentStatus === 'showUserInfo'" 
      :invite-info="inviteInfo"
      :current-user="currentUser"
      @switch-to-login="switchToLogin"  
      @join="toJoin"
    />
    <StatusCard v-else-if="currentStatus === 'joinSuccess'"
      :status="currentStatus"
      :title="'成功加入'"
      :desc="inviteInfo.marketName || inviteInfo.enterpriseName"
      :buttonTxt="'进入星辰RPA'"
      @click="openApp"
    />
    <StatusCard v-else-if="currentStatus === 'joined'"
      :status="currentStatus"
      :title="'您已经加入，无需重复加入。'"
      :desc="inviteInfo.marketName || inviteInfo.enterpriseName"
      :buttonTxt="'进入星辰RPA'"
      @click="openApp"
    />
    <StatusCard  v-if="currentStatus === 'reachLimited'"
      :status="currentStatus"
      :title="'已达免费邀请人数上限'"
      :desc="`请联系管理员升级`"
     /> 
  </div>
</template>
