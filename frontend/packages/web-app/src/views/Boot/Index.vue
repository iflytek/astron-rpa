<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import { base64ToString } from '@/utils/common'
import BUS from '@/utils/eventBus'
import { storage } from '@/utils/storage'

import ConfigProvider from '@/components/ConfigProvider/index.vue'
import BootHeader from '@/components/Boot/Header.vue'
import Loading from '@/components/Loading.vue'
import { utilsManager, windowManager } from '@/platform'
import { Auth } from '@rpa/components/auth'
import { getBaseURL } from '@/api/http/env'
import { theme } from 'ant-design-vue'
import LaunchCarousel from '@/components/Boot/LaunchCarousel.vue'

const { token } = theme.useToken()

const progress = ref(0)
const isLogin = ref(false)
 
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
  if(sessionStorage.getItem('launch') === '1')
    isLogin.value = true
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
      <Auth.LoginForm v-if="isLogin" :base-url="getBaseURL()" @finish="loginSuccess" />
    </Auth.PageLayout>
    <Loading />
  </ConfigProvider>
</template>
