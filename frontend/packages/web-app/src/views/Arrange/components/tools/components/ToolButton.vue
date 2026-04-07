<template>
  <rpa-hint-icon
    :name="props.icon"
    :title="props.tooltip"
    :size="props.size"
    :disabled="props.disabled"
    :color="props.color"
    class="mx-1"
    enable-hover-bg
    @click="$emit('click')"
  >
    <template #suffix>
      <span v-if="props.label" class="ml-1">{{ $t(props.label) }}</span>
    </template>
  </rpa-hint-icon>
</template>

<script setup lang="ts">
interface ToolButtonProps {
  icon: string
  label?: string
  tooltip?: string
  disabled?: boolean
  size?: string
  color?: string
}

const props = defineProps<ToolButtonProps>()
defineEmits<{ (e: 'click'): void }>()
</script>