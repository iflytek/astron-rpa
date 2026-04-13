<script setup lang="ts">
import { Divider } from 'ant-design-vue'
import { onMounted, ref } from 'vue'

import { isBrowser, windowManager } from '@/platform'

import WindowControls from './WindowControls.vue'

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
  platform: {
    type: String,
    default: (navigator.userAgent.includes('Macintosh') || navigator.userAgent.includes('Mac')) ? 'mac' : 'win',
  },
})

const isMaximized = ref(false)

function dbClickFn(e: MouseEvent) {
  if (props.dbtogglePrevent) {
    e.preventDefault()
    e.stopPropagation()
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
  <div data-tauri-drag-region class="app_control w-full drag shrink-0">
    <!-- Mac 样式的控制按钮放在左侧 -->
    <div
      v-if="props.platform === 'mac'"
      class="flex items-center no-drag h-full pl-2"
    >
      <WindowControls
        v-model:isMaximized="isMaximized"
        :minimize="props.minimize"
        :maximize="props.maximize"
        :close="props.close"
        :close-fn="props.closeFn"
        :platform="props.platform"
      />
    </div>

    <div
      data-tauri-drag-region
      class="app_control_text flex items-center gap-2 drag whitespace-nowrap"
      :class="{ 'pl-1': props.platform === 'mac' }"
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

      <!-- 窗口控制按钮 (Windows 样式放在右侧) -->
      <WindowControls
        v-if="props.platform === 'win'"
        v-model:isMaximized="isMaximized"
        :minimize="props.minimize"
        :maximize="props.maximize"
        :close="props.close"
        :close-fn="props.closeFn"
        :platform="props.platform"
      />
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
</style>
