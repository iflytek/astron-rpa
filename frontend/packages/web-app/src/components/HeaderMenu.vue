<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { useRoutePush } from '@/hooks/useCommonRoute'
import { useTopMenu } from '@/hooks/useTopMenu'

const siderMenu = useTopMenu() // 顶部菜单
const route = useRoute()

const currentKey = computed(() => route.matched[0].name)

function pushMenu(name: string, group: string) {
  if (group === currentKey.value)
    return
  useRoutePush({ name })
}
</script>

<template>
  <div data-tauri-drag-region class="flex items-center gap-1 no-drag">
    <span
      v-for="menu in siderMenu"
      :key="menu.group"
      class="menu_tab"
      :class="[{ menu_tab_active: currentKey === menu.group }]"
      @click="pushMenu(menu.name, menu.group)"
    >
      {{ $t(menu.group) }}
    </span>
  </div>
</template>

<style lang="scss" scoped>
.menu_tab {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-width: 76px;
  padding: 0 8px;
  height: 32px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 400;
  white-space: nowrap;

  &_active {
    font-weight: 500;
    background-color: $color-primary-bg;
  }

  &:not(&_active):hover {
    background-color: $color-fill-secondary;
  }
}
</style>
