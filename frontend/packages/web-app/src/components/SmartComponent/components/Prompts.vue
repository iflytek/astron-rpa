<script lang="ts" setup>
import { useDark } from '@vueuse/core'

interface PromptItem {
  key: string
  icon?: string
  label?: string
  description?: string
  disabled?: boolean
}

const props = defineProps<{
  items: PromptItem[]
  activeKey: string
}>()

const emit = defineEmits<{
  (evt: 'item-click', e: PromptItem)
}>()

const isDark = useDark()

function handleClick(prompt: PromptItem) {
  emit('item-click', prompt)
}
</script>

<template>
  <div class="flex justify-center gap-3">
    <div
      v-for="prompt in props.items"
      :key="prompt.key"
      :class="{ dark: isDark, active: activeKey === prompt.key }"
      class="prompt border border-[#000000]/[.1] dark:border-[#FFFFFF]/[.16] rounded-xl"
      @click="handleClick(prompt)"
    >
      <div class="flex gap-2 items-center font-medium">
        <rpa-icon :name="prompt.icon" size="20" />
        <span>{{ prompt.label }}</span>
      </div>
      <span>{{ prompt.description }}</span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.prompt {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  width: 264px;
  height: 77px;
  box-shadow:
    0 1px 2px 0 rgba(0, 0, 0, 0.03),
    0 1px 6px -1px rgba(0, 0, 0, 0.02),
    0 2px 4px 0 rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;

  &.active,
  &:hover {
    background-color: rgba(#d7d7ff, 0.4);
    border-color: #726fff;

    > div:nth-child(1) {
      color: $color-primary;
    }
  }
}

.dark.prompt {
  &.active,
  &:hover {
    background-color: rgba(#5d59ff, 0.35);
  }
}
</style>
