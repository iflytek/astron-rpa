<script setup lang="ts">
import { Divider } from 'ant-design-vue'
import { onMounted, ref } from 'vue'

import { isBrowser, windowManager } from '@/platform'

import { useCloseApp } from './HeaderControl/useCloseApp'

// 定义props
const props = defineProps({
  minimize: {
    type: Boolean,
    default: true,
  },
  maximize: {
    type: Boolean,
    default: true,
  },
  close: {
    type: Boolean,
    default: true,
  },
  title: {
    type: String,
    default: '',
  },
  closeFn: {
    type: Function,
    default: null,
  },
  dbtogglePrevent: {
    type: Boolean,
    default: false,
  },
})

const { closeApp } = useCloseApp()
const isMaximized = ref(true)

function dbClickFn(e: MouseEvent) {
  if (props.dbtogglePrevent) {
    e.preventDefault()
    e.stopPropagation()
  }
}

// 控制窗口最小化、最大化、关闭
function handleMinMaxClose(type: string) {
  if (isBrowser)
    return

  switch (type) {
    case 'minimize':
      windowManager.minimizeWindow()
      break
    case 'maximize':
      windowManager.maximizeWindow().then((isMax) => {
        isMaximized.value = isMax
      })
      break
    case 'close':
      handleClose()
      break
    default:
      break
  }
}
/**
 * 关闭窗口前，执行的操作
 */
function handleClose() {
  if (props.closeFn) {
    props.closeFn() // 自定义关闭函数
  }
  else {
    closeApp()
  }
}
onMounted(() => {
  windowManager.onWindowResize(() => {
    windowManager.isMaximized().then((isMax) => {
      isMaximized.value = isMax
    })
  })
})
</script>

<template>
  <div data-tauri-drag-region class="app_control w-full drag">
    <div
      data-tauri-drag-region
      class="app_control_text flex items-center gap-2 drag whitespace-nowrap"
      @dblclick="dbClickFn"
    >
      <img
        v-if="!title"
        data-tauri-drag-region
        class="w-5"
        src="/icons/icon.png"
        @dblclick="dbClickFn"
      >
      <span class="text-base leading-5 font-bold">
        {{ title || $t("app") }}
      </span>
    </div>
    <slot name="headMenu" />
    <div
      data-tauri-drag-region
      class="drag whitespace-nowrap flex-1 header-center"
      @dblclick="dbClickFn"
    >
      <slot name="headProject" />
    </div>
    <div
      data-tauri-drag-region
      class="flex items-center no-drag whitespace-nowrap h-full"
      @dblclick="dbClickFn"
    >
      <slot name="headControl" />

      <template v-if="$slots.headControl">
        <Divider type="vertical" />
      </template>

      <!-- 使用props控制显示 -->
      <span
        v-if="props.minimize"
        class="app_control__item"
        @click="handleMinMaxClose('minimize')"
      >
        <rpa-icon name="remove" />
      </span>
      <span
        v-if="props.maximize"
        class="app_control__item"
        @click="handleMinMaxClose('maximize')"
      >
        <rpa-icon :name="isMaximized ? 'middle' : 'maxwin'" />
      </span>
      <span
        v-if="props.close"
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
  position: fixed;
  top: 0;
  height: var(--headerHeight);
  z-index: var(--headerZindex);
  display: flex;
  align-items: center;
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
