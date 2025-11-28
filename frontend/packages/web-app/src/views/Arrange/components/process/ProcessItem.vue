<script lang="ts" setup>
import { useElementVisibility, useMouseInElement } from '@vueuse/core'
import { useTemplateRef, watch } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

import DropDownMenu from './DropdownMenu.vue'
import type { IMenuItem } from './DropdownMenu.vue'
import { ProcessActionEnum, useProcessMenuActions } from './hooks/useProcessMenus'

export interface ProcessItemState extends RPA.Process.ProcessModule {
  showDivider: boolean
}

interface ProcessItemProps {
  processItem: ProcessItemState
  isActive: boolean
}

const props = defineProps<ProcessItemProps>()

const emit = defineEmits<{(evt: 'visible-change', e: boolean): void}>()

const { canvasManager } = useProcessStore()
const target = useTemplateRef<HTMLDivElement>('target')
const isVisible = useElementVisibility(target, { threshold: 0.99 })
const isOutside = useMouseInElement(target).isOutside

watch(isVisible, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    emit('visible-change', newVal)
  }
})

const menus: IMenuItem[] = useProcessMenuActions({
  item: props.processItem,
  disabled: action => props.processItem.isMain && action !== ProcessActionEnum.CLOSE_ALL,
  actions: [
    ProcessActionEnum.OPEN,
    ProcessActionEnum.RENAME,
    ProcessActionEnum.COPY,
    ProcessActionEnum.SEARCH_CHILD_PROCESS,
    ProcessActionEnum.CLOSE_ALL,
    ProcessActionEnum.DELETE,
  ],
})

function clickProcessItem(isClose?: boolean) {
  // 先保存当前流程数据，再切换或关闭
  if (!isClose && props.isActive)
    return

  if (isClose) {
    canvasManager.closeTab(props.processItem.resourceId)
  } else {
    canvasManager.activateTab(props.processItem.resourceId)
  }
}
</script>

<template>
  <span
    ref="target"
    :key="processItem.resourceId"
    class="process-item min-w-[122px] max-w-[200px] max-h-[32px]"
    :class="props.isActive ? 'bg-white dark:bg-[#FFFFFF]/[.12]' : 'hover:bg-[#D7D7FF]/[.4] dark:hover:bg-[#5D59FF]/[.35]'"
    @click="clickProcessItem()"
  >
    <DropDownMenu :menus="menus" trigger="contextmenu">
      <span :class="['w-full flex items-center justify-between', { 'forbid': props.processItem.isMain }]">
        <span class="text-ellipsis whitespacw-nowrap overflow-hidden">
          {{ processItem.name }}
          <i v-if="processItem.isSaveing"> *</i>
        </span>
        <template v-if="!props.processItem.isMain">
          <rpa-hint-icon
            v-show="!isOutside && isVisible"
            name="close"
            size="14"
            class="p-1"
            @click.stop="clickProcessItem(true)"
          />
        </template>
      </span>
    </DropDownMenu>
    <div v-if="props.processItem.showDivider" class="divider bg-[#000000]/[.1] dark:bg-[#FFFFFF]/[.16]" />
  </span>
</template>

<style lang="scss" scoped>
.process-item {
  display: inline-flex;
  position: relative;
  padding: 8px 12px;
  border-radius: 8px 8px 0px 0px;
  cursor: pointer;

  .divider {
    position: absolute;
    right: 0;
    width: 1px;
    height: 14px;
  }
}
</style>
