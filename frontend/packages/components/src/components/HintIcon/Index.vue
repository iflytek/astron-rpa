<script lang="ts" setup>
import { createReusableTemplate } from '@vueuse/core'
import { Tooltip } from 'ant-design-vue'
import { computed } from 'vue'

import { Icon } from '../Icon'

export interface Props {
  name: string
  title?: string
  enableHoverBg?: boolean
  disabled?: boolean
  loading?: boolean
  size?: string
  width?: string
  height?: string
  spin?: boolean
  color?: string
  stroke?: string
  fill?: string
  iconClass?: string
}

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<Props>(), {
  size: '16',
  spin: false,
  enableHoverBg: false,
})

const emit = defineEmits<{
  (evt: 'click', e: MouseEvent): void
}>()

const [DefineTool, ReuseTool] = createReusableTemplate()

const iconProps = computed(() => {
  const { title, enableHoverBg, disabled, loading, color, ...filteredProps } = props
  return filteredProps
})

function handleClick(e: MouseEvent) {
  if (props.disabled || props.loading) {
    return
  }

  emit('click', e)
}
</script>

<template>
  <span
    v-bind="$attrs"
    :class="{
      'p-1 rounded': enableHoverBg,
      'hover:bg-[#F3F3F7] dark:hover:bg-[#FFFFFF]/[.08]': enableHoverBg && !disabled && !loading,
      '!cursor-not-allowed text-[#000000]/[.45] dark:text-[#FFFFFF]/[.45]': disabled,
      'cursor-pointer': !disabled,
      'loading': loading,
    }"
    class="inline-flex items-center select-none"
    :style="color ? { color } : {}"
    @click="handleClick"
  >

    <DefineTool>
      <span class="inline-flex items-center">
        <Icon v-if="loading" v-bind="iconProps" name="loading" class="outline-none" :class="iconClass" />
        <Icon v-else v-bind="iconProps" class="outline-none" :class="iconClass" />
        <slot name="suffix" />
      </span>
    </DefineTool>

    <Tooltip v-if="title && !disabled" :title="title">
      <ReuseTool />
    </Tooltip>
    <ReuseTool v-else />
  </span>
</template>

<style lang="scss" scoped>
@keyframes spin {
  from {
    -webkit-transform: rotate(0deg);
    transform: rotate(0deg);
  }

  to {
    -webkit-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}

.loading {
  opacity: 0.65;
  cursor: default;

  svg {
    animation: spin 1s linear infinite;
  }
}
</style>
