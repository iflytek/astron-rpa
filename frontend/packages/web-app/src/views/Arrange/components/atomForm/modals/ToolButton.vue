<script setup lang="ts">
interface ToolButtonProps {
  icon: string
  tooltip?: string
  title?: string
  size?: string
  disabled?: boolean
  color?: string
  class?: string
}

const props = withDefaults(defineProps<ToolButtonProps>(), {
  disabled: false,
  color: '',
  class: '',
})

const emit = defineEmits<{
  (evt: 'click', e: MouseEvent): void
}>()
</script>

<template>
  <rpa-hint-icon
    :name="icon"
    :title="props.tooltip"
    :size="props.size"
    :disabled="props.disabled"
    :color="props.color"
    class="mx-1"
    :class="props.class"
    enable-hover-bg
    @click="emit('click', $event)"
  >
    <template #suffix>
      <span v-if="props.title" class="ml-1">{{ $t(props.title) }}</span>
    </template>
  </rpa-hint-icon>
</template>
