<script setup lang="ts">
import { Auth } from '@rpa/components/auth'
import { theme } from 'ant-design-vue'
import { nextTick, onMounted, onUnmounted, ref } from 'vue'

import { base64ToString } from '@/utils/common'
import BUS from '@/utils/eventBus'
import { storage } from '@/utils/storage'

import { expiredModal, getBaseURL } from '@/api/http/env'
import BootHeader from '@/components/Boot/Header.vue'
import LaunchCarousel from '@/components/Boot/LaunchCarousel.vue'
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import Loading from '@/components/Loading.vue'
import { utilsManager, windowManager } from '@/platform'

const ENV = import.meta.env

const { token } = theme.useToken()

const progress = ref(0)
const isLogin = ref(false)
const loginFormRef = ref()

function loginWindowStep() {
  windowManager.restoreLoginWindow()
}

function launchProgressCallback(msg: { step: number }) {
  progress.value = msg.step
}

utilsManager.listenEvent('scheduler-event', (eventMsg) => {
  console.log('message: ', eventMsg)
  const msgString = base64ToString(eventMsg)
  const msgObject = JSON.parse(msgString)
  const { type, msg } = msgObject
  console.log('主进程消息: ', msgObject)
  switch (type) {
    case 'sync': {
      // 启动进度
      launchProgressCallback(msg)
      break
    }
    case 'sync_cancel': {
      storage.set('route_port', msg?.route_port)
      sessionStorage.setItem('launch', '1')
      loginAuto()
      break
    }
    default:
      break
  }
})

function loginAuto() {
  if (sessionStorage.getItem('launch') === '1') {
    isLogin.value = true
    const searchParams = new URLSearchParams(window.location.search)
    const code = searchParams.get('code')
    const tenantType = searchParams.get('tenantType')
    if (code === '900005') {
      expiredModal(tenantType)
      nextTick(() => {
        console.log(loginFormRef)
        if (tenantType === 'professional')
          loginFormRef.value.autoPreLogin()
      })
    }
  }
}

function loginSuccess(userInfo: any) {
  console.log('登录成功: ', userInfo)
  location.replace(`/`)
}

onMounted(() => {
  loginWindowStep()
})

window.onload = () => {
  loginAuto()
  utilsManager.invoke('main_window_onload').catch(() => {})
}

onUnmounted(() => {
  BUS.$off('launch-progress', launchProgressCallback)
})
</script>

<template>
  <ConfigProvider>
    <Auth.PageLayout>
      <template #header>
        <BootHeader />
      </template>
      <template v-if="!isLogin" #container>
        <div
          class="flex items-center justify-center"
        >
          <LaunchCarousel>
            <template #footer>
              <div class="mt-6 w-[280px]">
                <a-progress
                  :percent="progress"
                  :show-info="false"
                  :stroke-color="token.colorPrimary"
                  trail-color="rgba(255, 255, 255, 0.12)"
                />
              </div>
            </template>
          </LaunchCarousel>
        </div>
      </template>
      <Auth.LoginForm v-if="isLogin" ref="loginFormRef" :base-url="getBaseURL()" :auth-type="ENV.VITE_AUTH_TYPE || 'casdoor'" :edition="ENV.VITE_EDITION || 'saas'" @finish="loginSuccess" />
    </Auth.PageLayout>
    <Loading />
  </ConfigProvider>
</template>
