<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import { ProcessModal } from '@/views/Arrange/components/process'

import DropDownMenu from './DropdownMenu.vue'
import type { IMenuItem } from './DropdownMenu.vue'

const processModal = NiceModal.useModal(ProcessModal)

const menus: IMenuItem[] = [
  { key: 'createChildProcess', name: '新建子流程', fn: () => processModal.show({ type: 'process' }) },
  { key: 'createPyCode', name: '新建Python模块', fn: () => processModal.show({ type: 'module' }) },
]
</script>

<template>
  <DropDownMenu
    :menus="menus"
    trigger="click"
  >
    <rpa-hint-icon
      name="python-package-plus"
      class="hover:!bg-[#D7D7FF]/[.4] dark:hover:!bg-[#5D59FF]/[.35]"
      enable-hover-bg
    />
  </DropDownMenu>
</template>
