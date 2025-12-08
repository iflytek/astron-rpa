<script setup lang="ts">
import { Icon as RpaIcon } from '../../../Icon'

import { useTheme } from '../../../../theme'
const { setColorMode ,colorTheme } = useTheme()
</script>

<template>
  <div class="app_control w-full fixed top-0 left-0 h-[40px] flex items-center justify-between px-[20px] text-[#000000] dark:text-[#FFFFFF] z-[1000]">
    <div class="app_control_text flex items-center gap-2 whitespace-nowrap"  >
      <img
        class="w-5"
        src="/icons/icon.png"
      >
      <span class="text-base leading-5 font-bold">
        星辰RPA
      </span>
    </div>
    <div class="flex items-center no-drag whitespace-nowrap h-full">
      <RpaIcon class="cursor-pointer" name="theme-icon" @click="setColorMode(colorTheme === 'dark' ? 'light' : 'dark')"/>
    </div>
  </div>
</template>
