<script setup lang="ts">
import { EllipsisOutlined } from '@ant-design/icons-vue'

import DropDownMenu from './DropdownMenu.vue'
import type { IMenuItem } from './DropdownMenu.vue'
import { ProcessActionEnum, useProcessMenuActions } from './hooks/useProcessMenus'

const props = defineProps({
  data: {
    type: Object as () => RPA.Flow.ProcessModule,
    required: true,
  },
})

const emit = defineEmits(['close'])

const menus: IMenuItem[] = useProcessMenuActions({
  item: props.data,
  disabled: () => props.data.isMain,
  actions: [ProcessActionEnum.OPEN, ProcessActionEnum.RENAME, ProcessActionEnum.COPY, ProcessActionEnum.SEARCH_CHILD_PROCESS, ProcessActionEnum.DELETE],
})

function handleClick() {
  emit('close')
}
</script>

<template>
  <div class="text-xs flex items-center group">
    <span class="flex-1 truncate">{{ data.name }}</span>
    <DropDownMenu
      :menus="menus"
      trigger="click"
      @click="handleClick"
    >
      <EllipsisOutlined class="invisible group-hover:visible" @click.stop />
    </DropDownMenu>
  </div>
</template>
