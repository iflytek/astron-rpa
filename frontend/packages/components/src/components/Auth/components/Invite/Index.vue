<script setup lang="ts">
import type { AuthType, Edition, Platform } from '../../interface'
import InviteHeader from '../Base/InviteHeader.vue'
import StatusCard from '../Base/StatusCard.vue'
import Login from '../Login/Index.vue'

import { useInviteFlow } from './hooks/useInviteFlow'
import InviteUserInfo from './InviteUserInfo.vue'
import MobileInvite from './MobileInvite.vue'

const { baseUrl, edition, authType, platform } = defineProps({
  platform: { type: String as () => Platform },
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
  switchPage,
  login,
  toJoin,
  openApp,
} = useInviteFlow(emit)
</script>

<template>
  <div
    class="auth-container-content invite-container
    w-full h-[480px]
    md:w-[400px] md:h-[540px]"
  >
    <InviteHeader v-if="inviteInfo" class="block text-[#FFFFFF] pt-[84px] md:hidden" :invite-info="inviteInfo" />
    <MobileInvite v-if="currentStatus === 'init'" @accept="login" />
    <StatusCard
      v-if="currentStatus === 'linkExpired'"
      :status="currentStatus"
      title="邀请链接已失效"
      desc="请联系管理员获得新的链接"
    />
    <Transition name="slide-up">
      <Login v-if="currentStatus === 'needLogin'" :platform="platform" :base-url="baseUrl" :invite-info="inviteInfo" :edition="edition" :auth-type="authType" @finish="toJoin" />
    </Transition>
    <Transition name="slide-up">
      <InviteUserInfo
        v-if="currentStatus === 'showUserInfo'"
        :invite-info="inviteInfo"
        :current-user="currentUser"
        @switch-to-login="switchPage('needLogin')"
        @submit="toJoin"
      />
    </Transition>
    <StatusCard
      v-if="currentStatus === 'joinSuccess'"
      :status="currentStatus"
      title="成功加入"
      :desc="inviteInfo.marketName || inviteInfo.deptName"
      button-txt="进入星辰RPA"
      @click="openApp"
    />
    <StatusCard
      v-if="currentStatus === 'joined'"
      :status="currentStatus"
      title="您已经加入，无需重复加入"
      :desc="inviteInfo.marketName || inviteInfo.deptName"
      button-txt="进入星辰RPA"
      @click="openApp"
    />
    <StatusCard
      v-if="currentStatus === 'marketFull'"
      status="reachLimited"
      :title="`当前${inviteInfo.inviteType === 'market' ? '市场' : '空间'}人数已满`"
      :desc="`请联系${inviteInfo.inviteType === 'market' ? '市场' : '空间'}所有者处理`"
    />
    <StatusCard
      v-if="currentStatus === 'reachLimited'"
      :status="currentStatus"
      title="已达免费邀请人数上限"
      desc="请联系管理员升级"
    />
    <!-- 移动端点击遮罩层回到初始页面 -->
    <div
      v-if="currentStatus === 'needLogin' || currentStatus === 'showUserInfo'"
      class="fixed inset-0 bg-black/50 z-[998] md:hidden"
      @click="switchPage('init')"
    />
  </div>
</template>

<style scoped>
@media (max-width: 768px) {
  .slide-up-enter-active {
    transition:
      transform 0.3s ease-out,
      opacity 0.3s ease-out;
  }

  .slide-up-leave-active {
    transition:
      transform 0.3s ease-in,
      opacity 0.3s ease-in;
  }

  .slide-up-enter-from {
    transform: translateY(100%);
    opacity: 0;
  }

  .slide-up-leave-to {
    transform: translateY(100%);
    opacity: 0;
  }

  .slide-up-enter-to,
  .slide-up-leave-from {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (min-width: 769px) {
  .slide-up-enter-active,
  .slide-up-leave-active {
    transition: none;
  }
}
</style>
