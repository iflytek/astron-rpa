<script setup lang="ts">
import { Button } from '@/components/ui/button'

const props = withDefaults(defineProps<{
  testId?: string
  cancelLabel?: string
  submitLabel: string
  submitDisabled?: boolean
}>(), {
  testId: 'default',
  cancelLabel: '取消',
  submitDisabled: false,
})

const emit = defineEmits<{
  (e: 'cancel'): void
  (e: 'submit'): void
}>()
</script>

<template>
  <div
    :data-testid="`modal-action-bar-${props.testId}`"
    class="flex items-center justify-end gap-2 border-t border-[var(--ai-line-soft)] px-5 py-4"
  >
    <Button
      variant="secondary"
      class="h-9 rounded-[12px] border-[var(--ai-line)] bg-white px-4 text-black/58 shadow-none hover:bg-[var(--ai-surface-soft)] hover:translate-y-0"
      @click="emit('cancel')"
    >
      {{ props.cancelLabel }}
    </Button>
    <Button
      :disabled="props.submitDisabled"
      :variant="props.submitDisabled ? 'secondary' : 'default'"
      :class="props.submitDisabled ? 'bg-[#F2F4F8] text-black/28 shadow-none hover:bg-[#F2F4F8] hover:translate-y-0' : ''"
      class="h-9 rounded-[12px] px-4"
      @click="emit('submit')"
    >
      {{ props.submitLabel }}
    </Button>
  </div>
</template>
