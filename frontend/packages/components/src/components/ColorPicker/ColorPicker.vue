<script setup lang="ts">
import { PopoverProps } from 'ant-design-vue'
import { computed, ref, watch } from 'vue'
import type { CSSProperties } from 'vue'
import { createReusableTemplate } from '@vueuse/core'

import ColorPickerPanel from './ColorPickerPanel.vue'
import ColorPickerTrigger from './ColorPickerTrigger.vue'
import { isHex } from './utils'

export interface ColorPickerProps extends Pick<PopoverProps, 'placement' | 'trigger'> {
  defaultColors?: string[]
  style?: CSSProperties
  class?: string
  // Popover 相关属性
  disabled?: boolean
  // 是否显示触发器，如果为 false，则不显示 popover，直接显示颜色选择面板
  showTrigger?: boolean
  // 触发器大小
  size?: 'small' | 'middle' | 'large'
}

export interface ColorPickerEmits {
  (e: 'change', value: string): void
  (e: 'confirm', value: string): void
}

const modelValue = defineModel<string>({ default: '' })
const popoverOpen = defineModel<boolean>('open', { default: false })

const props = withDefaults(defineProps<ColorPickerProps>(), {
  defaultColors: () => [
    '#ff7e79',
    '#fefe7f',
    '#00ff81',
    '#007ffe',
    '#ff80c0',
    '#ff0104',
    '#00fcff',
    '#847cc2',
    '#fe00fe',
    '#7e0101',
    '#fc7f01',
    '#027e04',
    '#65b2f3',
    '#f9b714',
    '#068081',
    '#8305a1',
    '#b0cf29',
    '#0bfa49',
    '#9e255e',
    '#ffffff',
  ],
  trigger: 'click',
  disabled: false,
  showTrigger: true,
  size: 'middle',
})

const emit = defineEmits<ColorPickerEmits>()

const [DefineTemplate, ReuseTemplate] = createReusableTemplate()

const colorPickerPanelRef = ref<InstanceType<typeof ColorPickerPanel>>()

// 触发器颜色显示
const triggerColor = computed(() => {
  // 如果外部传入的 modelValue 是有效的 hex 颜色
  if (modelValue.value && isHex(modelValue.value)) {
    return modelValue.value
  }
  // 都没有则显示透明（配合网格背景显示）
  return 'transparent'
})


// 处理颜色变化（只在确认时触发）
function handleColorChange(value: string) {
  emit('change', value)
}

// 处理颜色确认
function handleColorConfirm(value: string) {
  modelValue.value = value
  emit('confirm', value)
}

// 处理关闭事件
function handleClose() {
  if (props.showTrigger) {
    popoverOpen.value = false
  }
}

// 监听 popover 打开状态，重新渲染颜色条
watch(popoverOpen, (isOpen) => {
  if (isOpen) {
    colorPickerPanelRef.value?.renderColorBar()
  }
})
</script>

<template>
  <DefineTemplate>
    <ColorPickerPanel
      ref="colorPickerPanelRef"
      :model-value="modelValue"
      :default-colors="defaultColors"
      :style="style"
      :class="class"
      :auto-close="true"
      @change="handleColorChange"
      @confirm="handleColorConfirm"
      @close="handleClose"
    />
  </DefineTemplate>

  <a-popover
    v-if="showTrigger"
    v-model:open="popoverOpen"
    :placement="placement"
    :trigger="trigger"
    :disabled="disabled"
    :destroy-tooltip-on-hide="true"
    :overlay-style="{ zIndex: 1001 }"
    class="color-picker-popover"
  >
    <template #content>
      <ReuseTemplate />
    </template>
    
    <slot name="trigger">
      <ColorPickerTrigger
        :color="triggerColor"
        :size="size"
        :disabled="disabled"
      />
    </slot>
  </a-popover>
  
  <ReuseTemplate v-else />
</template>
