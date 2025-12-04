<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import { base64ToString } from '@/utils/common'
import BUS from '@/utils/eventBus'
import { storage } from '@/utils/storage'

import ConfigProvider from '@/components/ConfigProvider/index.vue'
import Boot from '@/components/Boot/Index.vue'
import BootHeader from '@/components/Boot/Header.vue'
import Loading from '@/components/Loading.vue'
import { utilsManager, windowManager } from '@/platform'
import { Auth } from '@rpa/components/auth'
import { getBaseURL } from '@/api/http/env'

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
    <Boot v-if="!isLogin" :progress="progress" />
    <Auth.PageLayout v-else>
      <template #header>
        <BootHeader />
      </template>
      <Auth.LoginForm :base-url="getBaseURL()" @finish="loginSuccess" />
    </Auth.PageLayout>
    <Loading />
  </ConfigProvider>
</template>
