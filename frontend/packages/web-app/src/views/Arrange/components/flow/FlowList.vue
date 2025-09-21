<script setup lang="ts">
import { useElementVisibility, useEventBus, useScroll } from '@vueuse/core'
import { message } from 'ant-design-vue'
import { storeToRefs } from 'pinia'
import { computed, onBeforeUnmount, useTemplateRef, watch } from 'vue'

import { atomScrollIntoViewKey } from '@/constants/eventBusKey'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useFlowStore } from '@/stores/useFlowStore'
import { clearDraggable } from '@/views/Arrange/utils/drag'

import ContextMenu from './ContextMunus.vue'
import DraggableVirtualScroller from './DraggableVirtualScroller.vue'
import { addAtomData, draggableAddStyle, MAX_ATOM_NUM, moveAtomData } from './hooks/useFlow'
import { useRenderList, useRenderListProvide } from './hooks/useRenderList'
import { useRunDebug } from './hooks/useRunDebug'
import Item from './Item.vue'

const { colorTheme } = storeToRefs(useAppConfigStore())
const flowContainer = useTemplateRef<HTMLElement>('flowContainer')
const draggableRef = useTemplateRef('draggableRef')
const flowStore = useFlowStore()
const rawList = computed(() => flowStore.simpleFlowUIData)

useRenderListProvide(rawList)
const { renderList, adjustIndex, resetRenderList } = useRenderList()

// TODO: 这个实现有一定的局限性，如果后面原子能力列表改成虚拟滚动，需要换种实现方式
// 监听跳转按钮的可见性
const jumpIconIsVisible = useElementVisibility(() => document.getElementById(`jump-back__${flowStore.jumpFlowId}`))
// 监听原子能力列表的滚动事件，在滚动结束时如果存在跳转按钮的原子能力不可见，则隐藏跳转按钮
useScroll(flowContainer, {
  onStop: () => {
    if (flowStore.jumpFlowId && !jumpIconIsVisible.value) {
      flowStore.setJumpFlowId('')
    }
  },
})

const bus = useEventBus(atomScrollIntoViewKey)
bus.on((idOrIndex) => {
  draggableRef.value.scrollTo(idOrIndex)
})

useRunDebug()

function handleDragChange(e: any) {
  if (e.added) {
    const { element, newIndex } = e.added
    flowStore.setSimpleFlowUIDataByType(element, adjustIndex(newIndex, true), false)
    addAtomData(element.data.key, adjustIndex(newIndex, true), true)
  }
  else if (e.moved) {
    const { element, oldIndex, newIndex } = e.moved
    const data = flowStore.setSimpleFlowUIDataByType([], adjustIndex(oldIndex), true)
    flowStore.setSimpleFlowUIDataByType(data, adjustIndex(newIndex), false)

    moveAtomData(adjustIndex(oldIndex), adjustIndex(newIndex), element.id)
    resetRenderList() // 重置插入项位置
  }
}

async function triggerAdd(key: string, preIndex?: number) {
  addAtomData(key, preIndex)
}

watch(() => flowStore.simpleFlowUIData.length, (newLength) => {
  if (newLength > MAX_ATOM_NUM) {
    message.warning(`流程节点数量超出限制, 最大数量为{${MAX_ATOM_NUM}}，超出部分将不会进行保存`)
  }
})

onBeforeUnmount(() => {
  clearDraggable(draggableRef)
  flowStore.reset()
})
</script>

<template>
  <div
    id="listwrapper"
    ref="flowContainer"
    class="select-none before:bg-[#000000]/[.08] before:dark:bg-[#FFFFFF]/[.08] right-tab-close-area"
  >
    <DraggableVirtualScroller
      ref="draggableRef"
      v-slot="{ item, index }"
      :items="renderList"
      :min-item-size="40"
      :class="[colorTheme]"
      item-key="id"
      filter=".forbid"
      group="postTree"
      @start="draggableAddStyle"
      @move="draggableAddStyle"
      @change="handleDragChange"
    >
      <Item :key="item.id" :item="item" :index="index" @select="triggerAdd" />
    </DraggableVirtualScroller>
    <ContextMenu />
  </div>
</template>

<style lang="scss">
@import url('@/assets/css/list.scss');
</style>
