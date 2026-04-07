<script setup lang="ts">
import { onMounted } from 'vue'

import { useContextMenuList } from './utils/contextMenu'
import { useFlowState } from './hooks/useFlowState'
import ActionMenu from './ActionMenu.vue'

const { rightClickSelectedAtom, contextMenuVisible, flowManager, hideContextMenu } = useFlowState()
const menuItems = useContextMenuList()

const handleOpenChange = (visible: boolean) => {
  contextMenuVisible.value = visible
  !visible && hideContextMenu()
}

onMounted(() => {
  flowManager.on('shortcut', (shortcutKey: string) => {
    const target = Object.values(menuItems).find(i => i.shortcutKey === shortcutKey)
    const selectedAtoms = flowManager.getSelectedAtoms()

    target?.clickFn?.(selectedAtoms)
  })
})
</script>

<template>
  <a-dropdown :trigger="['contextmenu']" :open="contextMenuVisible" @open-change="handleOpenChange">
    <slot />
    <template v-if="rightClickSelectedAtom" #overlay>
      <ActionMenu :item="rightClickSelectedAtom" :show-shortcut-key="true" />
    </template>
  </a-dropdown>
</template>
