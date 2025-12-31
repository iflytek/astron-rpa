<script setup lang="ts">
import type { AuthType, Edition } from '../../interface'
import InviteUserInfo from '../Base/InviteUserInfo.vue'
import StatusCard from '../Base/StatusCard.vue'
import Login from '../Login/Index.vue'

import { useInviteFlow } from './hooks/useInviteFlow'

const { baseUrl, edition, authType } = defineProps({
  baseUrl: { type: String },
  edition: { type: String as () => Edition, default: 'saas' },
  authType: { type: String as () => AuthType, default: 'uap' },
})

const emit = defineEmits<{
  joinSuccess: []
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
    <StatusCard
      v-if="currentStatus === 'linkExpired'"
      :status="currentStatus"
      title="邀请链接已失效"
      desc="请联系管理员获得新的链接"
    />
    <Login v-else-if="currentStatus === 'needLogin'" :base-url="baseUrl" :invite-info="inviteInfo" :edition="edition" :auth-type="authType" @finish="toJoin" />
    <InviteUserInfo
      v-else-if="currentStatus === 'showUserInfo'"
      :invite-info="inviteInfo"
      :current-user="currentUser"
      @switch-to-login="switchToLogin"
      @join="toJoin"
    />
    <StatusCard
      v-else-if="currentStatus === 'joinSuccess'"
      :status="currentStatus"
      title="成功加入"
      :desc="inviteInfo.marketName || inviteInfo.enterpriseName"
      button-txt="进入星辰RPA"
      @click="openApp"
    />
    <StatusCard
      v-else-if="currentStatus === 'joined'"
      :status="currentStatus"
      title="您已经加入，无需重复加入。"
      :desc="inviteInfo.marketName || inviteInfo.enterpriseName"
      button-txt="进入星辰RPA"
      @click="openApp"
    />
    <StatusCard
      v-else-if="currentStatus === 'marketFull'"
      status="reachLimited"
      title="当前市场人数已满"
      desc="请联系市场所有者处理"
    />
    <StatusCard
      v-if="currentStatus === 'reachLimited'"
      :status="currentStatus"
      title="已达免费邀请人数上限"
      desc="请联系管理员升级"
    />
  </div>
</template>
