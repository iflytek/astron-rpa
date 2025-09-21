<script setup lang="ts">
import { menuConfig } from '../config'

const model = defineModel('value', { type: String })

function handleMenuClick(key: string) {
  model.value = key
}
</script>

<template>
  <a-menu class="h-full setting-menu flex flex-col gap-2" :selected-keys="[model]">
    <a-menu-item
      v-for="item in menuConfig"
      :key="item.key"
      @click="() => handleMenuClick(item.key)"
    >
      <div class="flex h-full items-center gap-2">
        <rpa-icon :name="item.icon" size="16px" />
        <span class="text-sm leading-5">{{ $t(item.name) }}</span>
      </div>
    </a-menu-item>
  </a-menu>
</template>

<style lang="scss" scoped>
.setting-menu {
  background-color: transparent;
  border-inline-end: none !important;
  min-width: 160px;
}

:deep(.ant-menu-item) {
  margin-inline: 0 !important;
  margin-block: 0 !important;
  width: 100% !important;
}
:deep(.ant-menu-item-selected) {
  color: inherit;
  font-weight: 500;
}
</style>
