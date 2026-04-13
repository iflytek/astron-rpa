<script setup lang="ts">
import { MacOSTrafficLight } from '@rpa/components'

import { isBrowser, windowManager } from '@/platform'
import { usePlatform } from '@/hooks/usePlatform'

const { isMac } = usePlatform()

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
</script>

<template>
  <div class="app_control w-full drag fixed top-0 left-0 pl-2">
    <MacOSTrafficLight
      v-if="isMac"
      class="px-3 no-drag"
      :close="true"
      :minimize="true"
      @close="handleMinMaxClose('close')"
      @minimize="handleMinMaxClose('minimize')"
    />

    <div class="app_control_text flex items-center gap-2 drag whitespace-nowrap">
      <img class="w-5" src="/icons/icon.png">
      <span class="text-base text-[#ffffff] leading-5 font-bold">
        {{ $t('app') }}
      </span>
    </div>
    <div
      v-if="!isMac"
      class="flex ml-auto items-center no-drag whitespace-nowrap h-full"
    >
      <!-- 使用props控制显示 -->
      <span
        class="app_control__item"
        @click="handleMinMaxClose('minimize')"
      >
        <rpa-icon name="remove" color="#ffffff" />
      </span>
      <span
        class="app_control__item"
        @click="handleMinMaxClose('close')"
      >
        <rpa-icon name="close" color="#ffffff" />
      </span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.app_control {
  height: var(--headerHeight);
  z-index: var(--headerZindex);
  display: flex;
  align-items: center;
  user-select: none;
  transition: all ease 0.2s;
  &_text {
    padding-left: 16px;
    user-select: none;
    min-width: 160px;
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
    background-color: #ffffff1f;
  }
  &:last-child:hover {
    background-color: red;
  }
}
</style>
