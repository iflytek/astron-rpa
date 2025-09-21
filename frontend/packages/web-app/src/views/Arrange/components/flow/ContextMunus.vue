<script setup lang="ts">
import { Divider } from 'ant-design-vue'
import { onBeforeUnmount, ref } from 'vue'

import { clickContextItem, disableContextMenuKeyboard, enableContextMenuKeyboard, getContextMenuList, getDisabled, getTitle, setContextMenu, toggleContextmenu } from '@/views/Arrange/utils/contextMenu'

const contextMenuInfo = ref({ visible: false, x: 0, y: 0, atom: null })
setContextMenu(contextMenuInfo)

const contextMenuList = getContextMenuList().filter(i => i.shortcutKey || i.type === 'divider').filter(i => !i.onlyShortcutKey)
const shortcutKeyList = getContextMenuList().filter(i => i.shortcutKey)
function hideContextMenu() {
  toggleContextmenu({ visible: false })
}
window.addEventListener('click', hideContextMenu)

// 快捷键注册
enableContextMenuKeyboard(shortcutKeyList)
// 快捷键注销
onBeforeUnmount(() => {
  window.removeEventListener('click', hideContextMenu)
  disableContextMenuKeyboard(shortcutKeyList)
})
</script>

<template>
  <div
    v-if="contextMenuInfo?.visible"
    class="customContextmenu bg-[#FFFFFF] dark:bg-[#1F1F1F]"
    :style="{ left: `${contextMenuInfo.x}px`, top: `${contextMenuInfo.y}px` }"
  >
    <template v-for="item in contextMenuList" :key="item.key">
      <Divider v-if="item.type === 'divider'" />
      <a-button
        v-else
        type="link"
        class="group flex justify-between gap-1 !px-[10px] items-center enabled:hover:bg-[#D7D7FF]/[.4] dark:enabled:hover:bg-[#5D59FF]/[.35] disabled:!text-[#000000]/[.25] dark:disabled:!text-[#FFFFFF]/[.25]"
        :disabled="getDisabled(item, contextMenuInfo.atom) || false"
        @click="() => clickContextItem(item, contextMenuInfo.atom)"
      >
        <div class="inline-flex items-center gap-1">
          <rpa-icon :name="item.icon" size="16" />
          {{ $t(getTitle(item, contextMenuInfo.atom)) }}
        </div>
        <div class="text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65] group-disabled:text-[#000000]/[.25] dark:group-disabled:text-[#FFFFFF]/[.25]">
          {{ item.shortcutKey }}
        </div>
      </a-button>
    </template>
  </div>
</template>
