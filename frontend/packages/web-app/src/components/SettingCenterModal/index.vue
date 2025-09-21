<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { computed, ref } from 'vue'

import SettingMenu from './components/settingMenu.vue'
import { menuConfig } from './config'

const modal = NiceModal.useModal()
const currentSettingWin = ref(menuConfig[0].key)

const activeMenu = computed(() => menuConfig.find(item => item.key === currentSettingWin.value))
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
      <SettingMenu v-model:value="currentSettingWin" />
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
