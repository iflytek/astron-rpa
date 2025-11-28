<script lang="ts" setup>
import { Icon, useTheme } from '@rpa/components'
import { computed, h } from 'vue'
import type { ItemType } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import { useContextMenuList, getDisabled, getTitle } from './utils/contextMenu'
import type { ContextMenuItem } from './utils/contextMenu'
import { useFlowState } from './hooks/useFlowState'

const props = defineProps<{ item: RPA.Atom, showShortcutKey?: boolean }>()

const { hideContextMenu } = useFlowState()
const { colorTheme } = useTheme()
const { t } = useTranslation()
const menuItems = useContextMenuList()

const genItem = (i: ContextMenuItem): ItemType => ({
  key: i.key,
  disabled: getDisabled(i, props.item) || false,
  icon: h(Icon, { name: i.icon, size: '16' }),
  label: h('div', { class: 'menu-item'}, [
    t(getTitle(i, props.item)),
    props.showShortcutKey && h('span', { class: 'menu-item-shortcut' }, [i.shortcutKey]),
  ]),
})

const menus = computed<ItemType[]>(() => {
  return [
    genItem(menuItems.runHere),
    genItem(menuItems.runDebug),
    genItem(menuItems.enableToggle),
    { type: 'divider' },
    genItem(menuItems.copy),
    genItem(menuItems.cut),
    genItem(menuItems.paste),
    { type: 'divider' },
    genItem(menuItems.mergeGroup),
    genItem(menuItems.unGroup),
    { type: 'divider' },
    genItem(menuItems.deleteNode),
  ]
})

function menuClick(key: string) {
  const target = Object.values(menuItems).find(i => i.key === key)
  target?.clickFn?.(props.item)
  hideContextMenu()
}

</script>

<template>
  <a-menu
    :items="menus"
    :class="[colorTheme, props.showShortcutKey ? 'min-w-[216px]' : 'min-w-[143px]']"
    class="!bg-white dark:!bg-[#1F1F1F]"
    mode="vertical"
    @click="({ key }) => menuClick(key as string)"
  />
</template>

<style lang="scss" scoped>
.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;

  &-shortcut {
    opacity: 0.65;
  }
}

:deep(.ant-dropdown-menu-item) {
  font-size: 12px;
  height: 28px;
  line-height: 28px;
  display: inline-flex;
  align-items: center;
  padding: 0 8px !important;
}

:deep(.ant-dropdown-menu-item .ant-dropdown-menu-title-content) {
  font-size: 12px !important;
}

:deep(.ant-dropdown-menu-item-active) {
  background-color: rgba(#d7d7ff, 0.4) !important;
}

.dark {
  :deep(.ant-dropdown-menu-item-active) {
    background-color: rgba(#5d59ff, 0.35) !important;
  }
}
</style>
