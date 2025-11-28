<script setup lang="ts">
export interface ColorPickerTriggerProps {
  color?: string
  size?: 'small' | 'middle' | 'large'
  disabled?: boolean
}

const props = withDefaults(defineProps<ColorPickerTriggerProps>(), {
  color: 'transparent',
  size: 'middle',
  disabled: false,
})
</script>

<template>
  <div
    class="color-picker-trigger border-border border"
    :class="[`color-picker-trigger-${props.size}`, { 'color-picker-trigger-disabled': disabled }]"
  >
    <span
      class="color-picker-trigger-inner"
      :style="{ backgroundColor: color }"
    />
  </div>
</template>

<style lang="scss" scoped>
// 触发器样式
.color-picker-trigger {
  cursor: pointer;
  border-radius: 4px;
  padding: 3px;
  transition: all 0.2s;
  box-sizing: border-box;

  &:hover:not(.color-picker-trigger-disabled) {
    border-color: var(--color-primary);
  }

  &.color-picker-trigger-disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }

  &.color-picker-trigger-small {
    width: 24px;
    height: 24px;
  }

  &.color-picker-trigger-middle {
    width: 32px;
    height: 32px;
  }

  &.color-picker-trigger-large {
    width: 40px;
    height: 40px;
  }

  .color-picker-trigger-inner {
    display: inline-flex;
    width: 100%;
    height: 100%;
    border-radius: 2px;
  }
}
</style>
