<script lang="ts" setup>
import { ref } from 'vue'

import ElementMenu from '@/components/ElementItemAction/elementMenu.vue'

const { activeDropdownMenuItemId } = defineProps({
  activeDropdownMenuItemId: {
    type: String,
    default: () => '',
  },
  configData: {
    type: Array<any>,
  },
})

const emits = defineEmits(['clickMenu'])

const open = ref(false)

function click(keys: Array<string>) {
  emits('clickMenu', keys)
}
</script>

<template>
  <div class="pick-item-action">
    <span v-for="confItem in configData" class="flex items-center">
      <a-tooltip v-if="confItem.type === 'tooltip'" :title="confItem.label" @click.stop="click([confItem.key])">
        <component :is="confItem.icon" />
      </a-tooltip>
      <a-dropdown v-if="confItem.type === 'dropdownMenus'" v-model:open="open" class="cursor-pointer">
        <template #overlay>
          <ElementMenu :selectd-id="activeDropdownMenuItemId" :menus="confItem.menus" @key-path="click" />
        </template>
        <component :is="confItem.icon" />
      </a-dropdown>
    </span>
  </div>
</template>

<style lang="scss" scoped>
.pick-item-action {
  text-align: center;
}

:deep(.anticon-edit),
:deep(.anticon-ellipsis),
:deep(.anticon) {
  font-size: 12px;
}

:deep(.anticon-delete) {
  margin-right: 5px;
}

:deep(.anticon-check) {
  position: absolute;
  right: 0;
  color: #4e68f6;
}

:deep(.ant-image) {
  height: 100%;
  display: inline-flex;
  align-items: center;
  background: #f8f8f8;
}

:deep(.ant-image-mask) {
  border-radius: 3px;
}
</style>
