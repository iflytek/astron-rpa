<script setup lang="ts">
import { Splitter } from '@rpa/components'
import { useElementSize } from '@vueuse/core'
import { onBeforeUnmount, reactive, useTemplateRef } from 'vue'

import {
  BOTTOM_BOOTLS_HEIGHT_DEFAULT,
  BOTTOM_BOOTLS_HEIGHT_SIZE_MIN,
  LEFT_BOOTLS_WIDTH_DEFAULT,
  LEFT_BOOTLS_WIDTH_SIZE_MAX,
  LEFT_BOOTLS_WIDTH_SIZE_MIN,
} from '@/constants'
import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'

import AtomTree from './components/atomTree/AtomTree.vue'
import BottomTools from './components/bottomTools/Index.vue'
import FlowContent from './components/flow/FlowContent.vue'
import ProcessHeader from './components/process/ProcessHeader.vue'
import RightTab from './components/rightTab/Index.vue'
import Search from './components/search/Index.vue'
import Tools from './components/tools/Tools.vue'
import useArrangeProvide from './hook/useArrangeProvide'

useArrangeProvide() // 注册表单全局数据

const processStore = useProcessStore()

const contentContainer = useTemplateRef<HTMLElement>('contentContainer')
const contentContainerSize = useElementSize(contentContainer)
const contentSplitterState = reactive({
  size: [undefined, BOTTOM_BOOTLS_HEIGHT_DEFAULT],
  collapsed: true,
})

const horizontalSpliterSize = reactive({
  size: [LEFT_BOOTLS_WIDTH_SIZE_MAX, undefined],
  collapseLeft: false,
})

useProjectDocStore().createProjectDoc() // 创建项目文档

onBeforeUnmount(() => {
  processStore.reset()
})

function handleSplitterResize(sizes: number[]) {
  contentSplitterState.size = sizes
}

function handleBottomToolsCollapsed(collapsed: boolean) {
  const height = collapsed ? BOTTOM_BOOTLS_HEIGHT_DEFAULT : BOTTOM_BOOTLS_HEIGHT_SIZE_MIN
  contentSplitterState.size = [contentContainerSize.height.value - height, height]
  contentSplitterState.collapsed = collapsed
}

function handleHorizontalSplitterResize(sizes: number[]) {
  horizontalSpliterSize.size = sizes
}

function handleLeftToolsCollapsed(collapsed: boolean) {
  const width = collapsed ? LEFT_BOOTLS_WIDTH_DEFAULT : LEFT_BOOTLS_WIDTH_SIZE_MAX
  horizontalSpliterSize.size[0] = width
  horizontalSpliterSize.collapseLeft = collapsed
}
</script>

<template>
  <a-layout class="flex-1 bg-[#ECEDF4] dark:bg-[#141414] text-[#000000]/[.85] dark:text-[#FFFFFF]/[.85] rounded-lg overflow-hidden">
    <Tools />
    <a-layout-content class="flex h-full gap-[2px]">
      <Splitter @resize="handleHorizontalSplitterResize">
        <Splitter.Panel
          :size="horizontalSpliterSize.size[0]"
          :min="LEFT_BOOTLS_WIDTH_SIZE_MIN"
          :max="LEFT_BOOTLS_WIDTH_SIZE_MAX"
          :resizable="!horizontalSpliterSize.collapseLeft"
        >
          <AtomTree :collapse="horizontalSpliterSize.collapseLeft" @collapse-left="handleLeftToolsCollapsed" />
        </Splitter.Panel>
        <Splitter.Panel :size="horizontalSpliterSize.size[1]">
          <div class="h-full flex gap-[2px]">
            <Splitter ref="contentContainer" layout="vertical" class="h-full flex-1 rounded-lg overflow-hidden" @resize="handleSplitterResize">
              <Splitter.Panel :size="contentSplitterState.size[0]">
                <div class="h-full flex flex-col">
                  <ProcessHeader />
                  <Search />
                  <FlowContent />
                </div>
              </Splitter.Panel>
              <Splitter.Panel
                :size="contentSplitterState.size[1]"
                :min="BOTTOM_BOOTLS_HEIGHT_SIZE_MIN"
                :resizable="!contentSplitterState.collapsed"
                class="!overflow-hidden"
              >
                <BottomTools
                  :height="contentSplitterState.size[1]"
                  :collapsed="contentSplitterState.collapsed"
                  @update:collapsed="handleBottomToolsCollapsed"
                />
              </Splitter.Panel>
            </Splitter>
            <RightTab />
          </div>
        </Splitter.Panel>
      </Splitter>
    </a-layout-content>
  </a-layout>
</template>

<style lang="scss" scoped>
:deep(.ant-tree-switcher-icon) {
  svg {
    vertical-align: baseline; // 树节点展开折叠图标垂直居中
  }
}
</style>
