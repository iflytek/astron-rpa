<script setup lang="ts">
import type { ItemType } from 'ant-design-vue'

defineProps<{ menus: ItemType[], selectdId: string }>()

const emits = defineEmits(['keyPath'])

function menuClick(path: Array<string>) {
  emits('keyPath', path)
}
</script>

<template>
  <a-menu
    class="pick-item-menu"
    :selected-keys="[]"
    mode="vertical"
    :items="menus"
    :get-popup-container="(triggerNode) => triggerNode.parentElement"
    @click="(item: any) => menuClick(item.keyPath)"
  />
</template>

<style lang="scss" scoped>
.pick-item-menu {
  min-width: 120px;
}
:deep(.ant-dropdown-menu-item),
:deep(.ant-menu-item) {
  height: 26px;
  line-height: 26px !important;
  font-size: 12px !important;
  font-weight: 400 !important;
}

:deep(.ant-dropdown-menu-submenu-title + div),
:deep(.ant-menu-submenu-title + div) {
  height: 0 !important;
}

:deep(.ant-dropdown-menu-submenu-title),
:deep(.ant-menu-submenu-title) {
  font-size: 12px !important;
  height: 26px;
  line-height: 26px !important;
  display: flex;
  align-items: center;
}
</style>
