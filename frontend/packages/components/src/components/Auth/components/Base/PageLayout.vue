<script setup lang="ts">
import { onBeforeUnmount } from 'vue'

import { useTheme } from '../../../../theme'
import LoginBgDark from '../../assets/imgs/login_bg_dark.png'
import loginImgUrl from '../../assets/imgs/login_img.svg'

import PageHeader from './PageHeader.vue'
import StarCanvas from './StarCanvas.vue'

const { colorTheme, setColorMode } = useTheme()

const loginImg = loginImgUrl
const loginBg = LoginBgDark

const color = colorTheme.value
setColorMode('light')
onBeforeUnmount(() => {
  setColorMode(color)
})
</script>

<template>
  <div class="auth-container w-full h-full bg-[#141414]" :class="[colorTheme]" :style="{ backgroundImage: `url(${loginBg})`, backgroundSize: '100% 100%' }">
    <slot name="header">
      <PageHeader />
    </slot>
    <div class="h-full relative z-[2] flex items-center justify-center">
      <slot name="container">
        <div class="flex items-center justify-between w-[920px] h-[540px]">
          <div class="text-[#FFFFFF] font-[600] font-sans">
            <div class="w-[480px] px-[20px] mb-[32px] text-center text-[32px]">
              <div class="w-full">
                <span class="text-[#726FFF] font-[600]">星辰RPA,</span>让重复自动化
              </div>
              <div class="w-full">
                让决策更智能
              </div>
            </div>
            <div class="w-[480px]">
              <object :data="loginImg" type="image/svg+xml" style="width: 100%; height: auto;" />
            </div>
          </div>
          <slot />
        </div>
      </slot>
    </div>
    <StarCanvas />
  </div>
</template>
