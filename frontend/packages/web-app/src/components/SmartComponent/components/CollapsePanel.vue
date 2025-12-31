<script lang="ts" setup>
defineProps<{
  title?: string
}>()

const collapse = defineModel('collapse', {
  type: Boolean,
  default: true,
})
</script>

<template>
  <div class="flex flex-col">
    <div class="flex items-center gap-1" @click="collapse = !collapse">
      <slot name="title" :collapse="collapse">
        <span>{{ title || (collapse ? '展开' : '收起') }}</span>
      </slot>
      <rpa-hint-icon name="chevron-down" class="text-text-tertiary" enable-hover-bg :class="[collapse ? 'rotate-0' : 'rotate-180']" />
    </div>
    <div class="transition-all" :class="{ 'h-0': collapse, 'hidden': collapse }">
      <a-divider class="!my-2" />
      <slot />
    </div>
  </div>
</template>
