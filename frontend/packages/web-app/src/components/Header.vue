<script setup lang="ts">
import { Divider } from 'ant-design-vue'
import { onMounted, ref } from 'vue'

import { windowManager } from '@/platform'
import { usePlatform } from '@/hooks/usePlatform'

import WindowControls from './WindowControls.vue'

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

const { isMac } = usePlatform()

const isMaximized = ref(true)

function dbClickFn(e: MouseEvent) {
  if (props.dbtogglePrevent) {
    e.preventDefault()
    e.stopPropagation()
  }
}

async function checkMaximized() {
  isMaximized.value = await windowManager.isMaximized()
}

onMounted(() => {
  checkMaximized();
  windowManager.onWindowResize(() => checkMaximized())
})
</script>

<template>
  <div data-tauri-drag-region class="app_control w-full drag shrink-0">
    <!-- Mac 样式的控制按钮放在左侧 -->
    <WindowControls
      v-if="isMac"
      class="pl-2"
      v-model:isMaximized="isMaximized"
      :minimize="props.minimize"
      :maximize="props.maximize"
      :close="props.close"
      :close-fn="props.closeFn"
    />

    <div
      data-tauri-drag-region
      class="app_control_text flex items-center gap-2 drag whitespace-nowrap"
      :class="{ 'pl-1': isMac }"
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
      :class="{ 'pr-2': isMac }"
      @dblclick="dbClickFn"
    >
      <slot name="headControl" />

      <template v-if="$slots.headControl && !isMac">
        <Divider type="vertical" />
      </template>

      <!-- 窗口控制按钮 (Windows 样式放在右侧) -->
      <WindowControls
        v-if="!isMac"
        v-model:isMaximized="isMaximized"
        :minimize="props.minimize"
        :maximize="props.maximize"
        :close="props.close"
        :close-fn="props.closeFn"
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
