<script setup lang="ts">
const props = defineProps<{ title: string }>()
</script>

<template>
  <div>
    <div class="flex items-center gap-[6px]">
      <span class="w-[2px] h-[12px] bg-primary" />
      <span>{{ props.title }}</span>
    </div>

    <div class="mt-4">
      <slot />
    </div>
  </div>
</template>
