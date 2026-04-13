<script setup lang="ts">
import { ref } from 'vue'

import { isBrowser, windowManager } from '@/platform'

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
  platform: {
    type: String,
    default: 'win', // 'win' | 'mac'
  },
})

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
  <div class="window-controls flex items-center no-drag h-full" :class="[`is-${platform}`]">
    <!-- Windows Style -->
    <template v-if="platform === 'win'">
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

    <!-- Mac Style -->
    <template v-else-if="platform === 'mac'">
      <div class="mac-controls-container flex items-center gap-2 px-3">
        <span
          v-if="props.close"
          class="mac-control-item mac-close"
          title="关闭"
          @click="handleMinMaxClose('close')"
        >
          <rpa-icon name="close" size="8" class="mac-icon" />
        </span>
        <span
          v-if="props.minimize"
          class="mac-control-item mac-minimize"
          title="最小化"
          @click="handleMinMaxClose('minimize')"
        >
          <rpa-icon name="remove" size="8" class="mac-icon" />
        </span>
        <span
          v-if="props.maximize"
          class="mac-control-item mac-maximize"
          :title="isMaximized ? '还原' : '最大化'"
          @click="handleMinMaxClose('maximize')"
        >
          <rpa-icon :name="isMaximized ? 'middle' : 'maxwin'" size="8" class="mac-icon" />
        </span>
      </div>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.window-controls {
  &.is-win {
    height: 100%;
  }
}

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

/* Mac Style */
.mac-controls-container {
  &:hover {
    .mac-icon {
      opacity: 1;
    }
  }
}

.mac-control-item {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;

  .mac-icon {
    opacity: 0;
    transition: opacity 0.2s;
    font-weight: bold;
    color: rgba(0, 0, 0, 0.5);
  }

  &.mac-close {
    background-color: #ff5f56;
    border: 0.5px solid #e0443e;
  }

  &.mac-minimize {
    background-color: #ffbd2e;
    border: 0.5px solid #dea123;
  }

  &.mac-maximize {
    background-color: #27c93f;
    border: 0.5px solid #1aab29;
  }
}
</style>
