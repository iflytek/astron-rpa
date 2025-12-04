<script setup lang="ts">
import type { CarouselRef } from 'ant-design-vue/es/carousel'
import { Carousel } from 'ant-design-vue'
import { ref, useTemplateRef } from 'vue'
import { useTheme } from '../../theme'
import { illustrationList } from './launch'
import { Icon as RpaIcon } from '../Icon'

const { colorTheme } = useTheme()

const carouselRef = useTemplateRef<CarouselRef>('carouselRef')
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
</script>

<template>
  <div class="w-[400px] flex flex-col items-center">
    <Carousel
      ref="carouselRef"
      :after-change="onChange"
      autoplay
      :dots="false"
      effect="fade"
      class="w-[376px]"
    >
      <RpaIcon
        v-for="(item, index) in randomIllustrationGroup"
        :key="index"
        :name="`${colorTheme}-${item.img}`"
        width="100%"
        height="235px"
      />
    </Carousel>

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
      {{ randomIllustrationGroup?.[current]?.text }}
    </div>
    <div class="mt-[6px] text-sm leading-[22px]">
      {{ randomIllustrationGroup?.[current]?.desc }}
    </div>
    <slot name="footer"></slot>
  </div>
 </template>

<style lang="scss" scoped>
</style>
