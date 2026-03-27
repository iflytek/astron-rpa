<script setup lang="ts">
const props = defineProps<{
  modelValue: string | number
  options: readonly { value: string | number, label: string }[]
  testId?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()
</script>

<template>
  <div
    :data-testid="props.testId"
    class="inline-flex rounded-full bg-[#EEF2F7] p-1"
  >
    <button
      v-for="option in props.options"
      :key="String(option.value)"
      type="button"
      class="rounded-full px-3 py-1.5 text-[12px] leading-4 transition-all"
      :class="props.modelValue === option.value
        ? 'bg-white text-[#1A1A2E] shadow-[0_6px_14px_rgba(15,23,42,0.06)]'
        : 'text-black/44 hover:text-black/62'"
      @click="emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>
