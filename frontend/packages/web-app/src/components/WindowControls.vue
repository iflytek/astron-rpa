<script setup lang="ts">
import { MacOSTrafficLight } from '@rpa/components'

import { isBrowser, windowManager } from '@/platform'
import { usePlatform } from '@/hooks/usePlatform'

import { useCloseApp } from './HeaderControl/useCloseApp'

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
  isMaximized: {
    type: Boolean,
    default: false,
  },
  closeFn: {
    type: Function,
    default: null,
  },
})

const { isMac } = usePlatform()

const emit = defineEmits(['update:isMaximized'])

const { closeApp } = useCloseApp()

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
        emit('update:isMaximized', isMax)
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
</script>

<template>
  <div class="window-controls flex items-center no-drag h-full">
    <!-- Mac Style -->
    <template v-if="isMac">
      <MacOSTrafficLight
        class="px-3"
        :close="props.close"
        :minimize="props.minimize"
        :maximize="props.maximize"
        :is-maximized="props.isMaximized"
        @close="handleMinMaxClose('close')"
        @minimize="handleMinMaxClose('minimize')"
        @maximize="handleMinMaxClose('maximize')"
      />
    </template>

    <!-- Windows Style -->
    <template v-else>
      <span
        v-if="props.minimize"
        class="win-control-item"
        title="最小化"
        @click="handleMinMaxClose('minimize')"
      >
        <rpa-icon name="remove" />
      </span>
      <span
        v-if="props.maximize"
        class="win-control-item"
        :title="isMaximized ? '还原' : '最大化'"
        @click="handleMinMaxClose('maximize')"
      >
        <rpa-icon :name="isMaximized ? 'middle' : 'maxwin'" />
      </span>
      <span
        v-if="props.close"
        class="win-control-item close-btn"
        title="关闭"
        @click="handleMinMaxClose('close')"
      >
        <rpa-icon name="close" />
      </span>
    </template>
  </div>
</template>

<style lang="scss" scoped>
/* Windows Style */
.win-control-item {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 40px;
  transition: background-color 0.2s;

  &:hover {
    background-color: $color-fill-secondary;
  }

  &.close-btn:hover {
    background-color: #e81123;
    color: white;
  }
}
</style>
