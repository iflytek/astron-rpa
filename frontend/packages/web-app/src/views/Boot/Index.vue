<script setup lang="ts">
import { theme } from 'ant-design-vue'
import type { CarouselRef } from 'ant-design-vue/es/carousel'
import { onMounted, onUnmounted, ref, useTemplateRef } from 'vue'

import BUS from '@/utils/eventBus'
import { storage } from '@/utils/storage'

import authService from '@/auth/index'
import Header from '@/components/Header.vue'
import { illustrationList } from '@/constants/launch'
import { DESIGNER } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { windowManager } from '@/platform'
import { useAppConfigStore } from '@/stores/useAppConfig'

const appConfigStore = useAppConfigStore()

const { token } = theme.useToken()

const carouselRef = useTemplateRef<CarouselRef>('carouselRef')
const progress = ref(0)
const current = ref(0)

// 从 illustrationList 中随机挑一组
const randomIllustrationGroup
  = illustrationList[Math.floor(Math.random() * illustrationList.length)]

if (storage.get('httpReady', 'sessionStorage') === 'true') {
  authService.init()
  authService.getAuth().checkLogin(() => {
    useRoutePush({ name: DESIGNER })
  })
}

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

BUS.$on('launch-progress', launchProgressCallback)

onMounted(() => {
  loginWindowStep()
})

onUnmounted(() => {
  BUS.$off('launch-progress', launchProgressCallback)
})
</script>

<template>
  <div class="flex flex-col w-full h-full bg-[#ECEDF4] dark:bg-[#141414]">
    <Header :maximize="false" class="!relative" />

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
            :name="`${appConfigStore.colorTheme}-${item.img}`"
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
  </div>
</template>
