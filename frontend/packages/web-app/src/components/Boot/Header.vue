<script setup lang="ts">
import { isBrowser, windowManager } from '@/platform'
import { useTheme } from '@rpa/components'

const { setColorMode, colorTheme } = useTheme()

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
      <span
        class="app_control__item"
        @click="setColorMode(colorTheme === 'dark' ? 'light' : 'dark')"
      >
        <rpa-icon name="theme-icon" />
      </span>
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
    background-color: $color-fill-secondary;
  }
  &:last-child:hover {
    background-color: red;
  }
}
</style>
