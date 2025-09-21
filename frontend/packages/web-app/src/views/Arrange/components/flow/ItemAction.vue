<script lang="ts" setup>
import { Icon } from '@rpa/components'
import type { ItemType } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { storeToRefs } from 'pinia'
import { computed, h } from 'vue'

import { useAppConfigStore } from '@/stores/useAppConfig'
import { clickContextItem, getContextMenuList, getDisabled, getTitle } from '@/views/Arrange/utils/contextMenu'

const { item } = defineProps<{ item: RPA.Atom }>()

const { t } = useTranslation()
const { colorTheme } = storeToRefs(useAppConfigStore())

const menuList = getContextMenuList()

const menus = computed<ItemType[]>(() => {
  return menuList.filter(i => !i.onlyShortcutKey).map((i) => {
    const isDivider = i.type === 'divider'

    if (isDivider) {
      return { type: 'divider' }
    }

    return {
      key: i.key as string,
      disabled: getDisabled(i, item) || false,
      icon: h(Icon, { name: i.icon, size: '16' }),
      label: t(getTitle(i, item)),
      originItem: i,
    }
  })
})

const btnList = computed(() => menuList.filter(i => !i.onlyShortcutKey && i.actionOper))

function actionClick(contextItem: any) {
  clickContextItem(contextItem, item, 'action')
}

function menuClick(key: string) {
  const target = menuList.find(i => i.key === key)
  if (target) {
    actionClick(target)
  }
}
</script>

<template>
  <div class="flow-list-item-action">
    <template v-for="citem in btnList" :key="citem.key">
      <rpa-hint-icon
        :name="citem.actionicon || citem.icon"
        :title="$t(getTitle(citem, item))"
        :disabled="getDisabled(citem, item)"
        class="mr-[12px]"
        @click="() => actionClick(citem)"
      />
    </template>
    <a-dropdown class="cursor-pointer" placement="bottom">
      <template #overlay>
        <a-menu
          :items="menus"
          :class="[colorTheme]"
          class="w-[143px] !bg-white dark:!bg-[#1F1F1F]"
          mode="vertical"
          @click="({ key }) => menuClick(key as string)"
        />
      </template>
      <rpa-hint-icon name="ellipsis" />
    </a-dropdown>
  </div>
</template>

<style lang="scss" scoped>
:deep(.ant-dropdown-menu-item) {
  font-size: 12px;
  height: 28px;
  line-height: 28px;
  display: inline-flex;
  align-items: center;
  padding: 0 4px !important;
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
