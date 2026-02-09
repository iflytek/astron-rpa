<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { isEmpty } from 'lodash-es'
import { computed, ref } from 'vue'

import { extensions } from '@/plugins/extension'

import SettingMenu from './components/settingMenu.vue'
import type { MenuItem } from './config'
import { menuConfig } from './config'

const modal = NiceModal.useModal()
const currentSettingWin = ref(menuConfig[0].key)

const menuItems = computed(() => {
  const pluginItems: MenuItem[] = (extensions?.settings.getAll() ?? []).map(item => ({
    key: item.id,
    icon: item.icon,
    name: item.title,
    component: item.content,
  }))

  if (isEmpty(pluginItems)) {
    return menuConfig
  }

  return [...menuConfig, ...pluginItems]
})

const activeMenu = computed(() => menuItems.value.find(item => item.key === currentSettingWin.value))
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('setupCenter')"
    :z-index="99"
    :width="960"
    :footer="null"
  >
    <div class="flex h-[500px] gap-4 py-3">
      <SettingMenu v-model:value="currentSettingWin" :items="menuItems" />
      <div class="setmodal-content flex-1">
        <component :is="activeMenu.component" />
      </div>
    </div>
  </a-modal>
</template>

<style lang="scss" scoped>
.setmodal-content {
  overflow-x: hidden;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 0;
  }
}
</style>
