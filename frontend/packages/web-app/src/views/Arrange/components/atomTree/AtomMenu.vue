<script setup lang="ts">
import type { ATOMTABKEYS } from '@/views/Arrange/config/atom'
import { ATOMTABS } from '@/views/Arrange/config/atom'

const activeTab = defineModel<ATOMTABKEYS>('value', { default: ATOMTABS[0].value })
</script>

<template>
  <a-segmented v-model:value="activeTab" block :options="ATOMTABS" class="mx-3">
    <template #label="{ title }">
      <span class="text-[12px]">{{ $t(title) }}</span>
    </template>
  </a-segmented>
</template>
