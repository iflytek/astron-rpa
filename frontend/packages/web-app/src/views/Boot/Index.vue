<script setup lang="ts">
import { theme } from 'ant-design-vue'
import type { CarouselRef } from 'ant-design-vue/es/carousel'
import { onMounted, onUnmounted, ref, useTemplateRef } from 'vue'
import { useTheme } from '@rpa/components'

import { base64ToString } from '@/utils/common'
import BUS from '@/utils/eventBus'
import { storage } from '@/utils/storage'

import authService from '@/auth/index'
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import Loading from '@/components/Loading.vue'
import { illustrationList } from '@/constants/launch'
import { isBrowser, utilsManager, windowManager } from '@/platform'

const { colorTheme } = useTheme()
const { token } = theme.useToken()

const carouselRef = useTemplateRef<CarouselRef>('carouselRef')
const progress = ref(0)
const current = ref(0)

// 从 illustrationList 中随机挑一组
const randomIllustrationGroup
  = illustrationList[Math.floor(Math.random() * illustrationList.length)]

function onChange(idx: number) {
  current.value = idx
}

function onSwitch(idx: number) {
  current.value = idx
  carouselRef.value?.goTo(idx)
}

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
      loginAuto()
      break
    }
    default:
      break
  }
})

function loginAuto() {
  authService.getAuth().checkLogin(() => {
    location.replace(`/`)
  })
}

// 控制窗口最小化、最大化、关闭
function handleMinMaxClose(type: string) {
  if (isBrowser)
    return

  switch (type) {
    case 'minimize':
      windowManager.minimizeWindow()
      break
    case 'close':
      windowManager.closeWindow()
      break
    default:
      break
  }
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
    <div class="flex flex-col w-full h-full bg-[#ECEDF4] dark:bg-[#141414]">
      <div data-tauri-drag-region class="app_control w-full drag">
        <div
          data-tauri-drag-region
          class="app_control_text flex items-center gap-2 drag whitespace-nowrap"
        >
          <img data-tauri-drag-region class="w-5" src="/icons/icon.png">
          <span class="text-base leading-5 font-bold">
            {{ $t('app') }}
          </span>
        </div>
        <div
          data-tauri-drag-region
          class="flex items-center no-drag whitespace-nowrap h-full"
        >
          <!-- 使用props控制显示 -->
          <span
            class="app_control__item"
            @click="handleMinMaxClose('minimize')"
          >
            <rpa-icon name="remove" />
          </span>
          <span
            class="app_control__item"
            @click="handleMinMaxClose('close')"
          >
            <rpa-icon name="close" />
          </span>
        </div>
      </div>
      <div
        class="flex-1 bg-[#ffffff] dark:bg-[#1D1D1D] flex items-center justify-center"
      >
        <div class="w-[400px] flex flex-col items-center">
          <a-carousel
            ref="carouselRef"
            :after-change="onChange"
            autoplay
            :dots="false"
            effect="fade"
            class="w-[320px]"
          >
            <rpa-icon
              v-for="(item, index) in randomIllustrationGroup"
              :key="index"
              :name="`${colorTheme}-${item.img}`"
              width="100%"
              height="200px"
            />
          </a-carousel>

          <div class="mt-4 flex items-center justify-center gap-2">
            <span
              v-for="(_, index) in randomIllustrationGroup"
              :key="index"
              class="w-2 h-2 rounded cursor-pointer bg-[rgba(0,0,0,0.10)] dark:bg-[rgba(255,255,255,0.25)]"
              :class="{ '!bg-primary': index === current }"
              @click="onSwitch(index)"
            />
          </div>

          <div class="mt-5 text-base leading-[22px] font-medium">
            {{ randomIllustrationGroup[current].text }}
          </div>
          <div class="mt-[6px] text-sm leading-[22px]">
            {{ randomIllustrationGroup[current].desc }}
          </div>

          <div class="mt-6 w-[280px]">
            <a-progress
              :percent="progress"
              :show-info="false"
              :stroke-color="token.colorPrimary"
            />
          </div>
        </div>
      </div>
      <Loading />
    </div>
  </ConfigProvider>
</template>

<style lang="scss" scoped>
.app_control {
  position: relative;
  top: 0;
  height: var(--headerHeight);
  z-index: var(--headerZindex);
  display: flex;
  align-items: center;
  justify-content: space-between;
  user-select: none;
  transition: all ease 0.2s;

  &_text {
    padding-left: 16px;
    user-select: none;
    width: 160px;
  }
}

.app_control__item {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 40px;
  &:hover {
    background-color: $color-fill-secondary;
  }
  &:last-child:hover {
    background-color: red;
  }
}
</style>
