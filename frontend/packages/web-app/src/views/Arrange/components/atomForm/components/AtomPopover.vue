<script setup lang="ts">
interface Props {
  tooltip?: string
}

const open = defineModel<boolean>('open', { required: true })
const props = defineProps<Props>()
</script>

<template>
  <a-popover
    v-model:open="open"
    class="atom-popover"
    placement="topLeft"
    trigger="click"
    :overlay-style="{ zIndex: 1001 }"
  >
    <template #content>
      <slot name="content" />
    </template>

    <a-tooltip v-if="props.tooltip" :title="props.tooltip">
      <slot />
    </a-tooltip>
    <slot v-else />
  </a-popover>
</template>

<style lang="scss" scoped>
.atom-popover {
  .atom-popover-footer {
    border-top: 1px solid #f0f0f0;
  }
}

:deep(.ant-popover) {
  display: none;
}

:deep(.ant-popover-content) {
  display: none;
}
</style>
