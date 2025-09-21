<script setup lang="ts">
import { createReusableTemplate } from '@vueuse/core'
import { isFunction } from 'lodash-es'
import { computed } from 'vue'

import useProjectDocStore from '@/stores/useProjectDocStore'
import { useRunningStore } from '@/stores/useRunningStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

import ProjectName from '../../components/projectName/Index.vue'

import { useHotkey } from './hooks/useHotkey'
import { useToolsBack } from './hooks/useToolsBack'
import { useToolsCustomComp } from './hooks/useToolsCustomComp'
import { useToolsDataPick } from './hooks/useToolsDataPick'
import { useToolsDebug } from './hooks/useToolsDebug'
import { useToolsDebugContinue } from './hooks/useToolsDebugContinue'
import { useToolsDebugNextStep } from './hooks/useToolsDebugNextStep'
import { useToolsGroup } from './hooks/useToolsGroup'
import { useToolsMultiSelect } from './hooks/useToolsMultiSelect'
import { useToolsPublish } from './hooks/useToolsPublish'
import { useToolsRecorder } from './hooks/useToolsRecorder'
import { useToolsRedo } from './hooks/useToolsRedo'
import { useToolsRun } from './hooks/useToolsRun'
import { useToolsSave } from './hooks/useToolsSave'
import { useToolsStop } from './hooks/useToolsStop'
import { useToolsUndo } from './hooks/useToolsUndo'
import { useToolsUnGroup } from './hooks/useToolsUnGroup'

type CheckFn = boolean | ((data: { status: string, isBreak?: boolean, canUndo?: boolean, canRestore?: boolean }) => boolean)

function toolBtnFn(fn: CheckFn, data: { status: string, isBreak?: boolean, canUndo?: boolean, canRestore?: boolean }): boolean {
  return typeof fn === 'function' ? fn(data) : fn || false
}

// const toolsSaveTemplate = useToolsSaveTemplate()
// const toolsKeyManagement = useToolsKeyManagement()

const btnList = [
  useToolsSave(),
  useToolsBack(),
  useToolsPublish(),
  useToolsRun(),
  useToolsDebug(),
  useToolsDebugContinue(),
  useToolsDebugNextStep(),
  useToolsStop(),
  useToolsUndo(),
  useToolsRedo(),
  useToolsRecorder(),
  useToolsDataPick(),
  useToolsGroup(),
  useToolsUnGroup(),
  useToolsMultiSelect(),
  useToolsCustomComp(),
]

const [
  toolsSave,
  toolsBack,
  toolsPublish,
  toolsRun,
  toolDebug,
  toolDebugContinue,
  toolDebugNextStep,
  toolStop,
  toolsUndo,
  toolsRedo,
  toolsRecorder,
  toolsDataPick,
  toolsGroup,
  toolsUnGroup,
  toolsMultiSelect,
  toolsCustomComp,
] = btnList.map(tool => getComputedTool(tool))

function getComputedTool(tool: ArrangeTools) {
  return computed(() => {
    const runningStatus = useRunningStore().running
    const isBreak = useRunningStore().debugData?.is_break || false
    const canUndo = useProjectDocStore().canUndo || false
    const canRestore = useProjectDocStore().canRestore || false
    return {
      ...tool,
      show: toolBtnFn(tool.show, { status: runningStatus }),
      disable: toolBtnFn(tool.disable, { status: runningStatus, isBreak, canUndo, canRestore }),
    }
  })
}

function toolItemFn(item: ArrangeTools) {
  const runningStatus = useRunningStore().running
  const isBreak = useRunningStore().debugData?.is_break || false
  const canUndo = useProjectDocStore().canUndo || false
  const canRestore = useProjectDocStore().canRestore || false

  const bol = isFunction(item.validateFn)
    ? item.validateFn({
        disable: toolBtnFn(item.disable, { status: runningStatus, isBreak, canUndo, canRestore }),
        show: toolBtnFn(item.show, { status: runningStatus }),
      })
    : true

  bol && item.clickFn?.()
}

useHotkey(btnList, toolItemFn)

const [DefineTool, ReuseTool] = createReusableTemplate<{ item: ReturnType<typeof getComputedTool>['value'] }>()
</script>

<template>
  <DefineTool v-slot="{ item }">
    <rpa-hint-icon
      v-if="item.show"
      :key="item.key"
      :name="item.icon"
      :title="$t(isFunction(item.title) ? item.title() : item.title)"
      :size="item.fontSize"
      :disabled="item.disable"
      :color="item.color"
      class="mx-1"
      :class="[item.class]"
      enable-hover-bg
      @click="() => !item.disable && toolItemFn(item)"
    >
      <template #suffix>
        <span v-if="item.name" class="ml-1">{{ $t(item.name) }}</span>
      </template>
    </rpa-hint-icon>
  </DefineTool>

  <nav class="tools flex items-center justify-between bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.04] rounded-lg right-tab-close-area">
    <section class="tools-box flex items-center justify-center">
      <ProjectName>
        <template #prefix>
          <ReuseTool :item="toolsBack" class="!mx-0 !p-0" />
        </template>
      </ProjectName>
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <ReuseTool :item="toolsUndo" />
      <ReuseTool :item="toolsRedo" />
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <ReuseTool :item="toolsMultiSelect" class="editor-tool" />
      <ReuseTool :item="toolsGroup" class="editor-tool" />
      <ReuseTool :item="toolsUnGroup" class="editor-tool" />
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <ReuseTool :item="toolsRecorder" />
      <ReuseTool :item="toolsDataPick" />
      <ReuseTool :item="toolsCustomComp" />
    </section>
    <section class="tools-box flex items-center justify-center">
      <ReuseTool :item="toolDebug" />
      <ReuseTool :item="toolDebugContinue" />
      <ReuseTool :item="toolDebugNextStep" />
      <ReuseTool :item="toolStop" />
      <ReuseTool :item="toolsRun" />
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <ReuseTool :item="toolsSave" />
      <ReuseTool :item="toolsPublish" />
    </section>
  </nav>
</template>

<style lang="scss" scoped>
.tools {
  height: 48px;
  width: 100%;
  margin-bottom: 2px;
}
</style>
