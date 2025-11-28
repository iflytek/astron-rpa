<script lang="ts" setup>
import ActionMenu from './ActionMenu.vue'
import type { ContextMenuItem } from './utils/contextMenu'
import { useContextMenuList, getDisabled, getTitle } from './utils/contextMenu'

const { item } = defineProps<{ item: RPA.Atom }>()

const { runDebug, deleteNode } = useContextMenuList()

function actionClick(contextItem: ContextMenuItem) {
  contextItem.clickFn?.(item)
}
</script>

<template>
  <div class="flow-list-item-action">
    <template v-for="citem in [runDebug, deleteNode]" :key="citem.key">
      <rpa-hint-icon
        :name="citem.actionicon || citem.icon"
        :title="$t(getTitle(citem, item))"
        :disabled="getDisabled(citem, item)"
        class="mr-[12px]"
        @click.stop="() => actionClick(citem)"
      />
    </template>
    <a-dropdown class="cursor-pointer" placement="bottom">
      <template #overlay>
        <ActionMenu :item="item" />
      </template>
      <rpa-hint-icon name="ellipsis" />
    </a-dropdown>
  </div>
</template>
