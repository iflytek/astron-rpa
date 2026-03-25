<script setup lang="ts">
import ProjectName from '../../components/projectName/Index.vue'

import ToolRedo from './buttons/ToolRedo.vue'
import ToolUndo from './buttons/ToolUndo.vue'
import ToolSave from './buttons/ToolSave.vue'
import ToolPublish from './buttons/ToolPublish.vue'
import ToolRun from './buttons/ToolRun.vue'
import ToolStop from './buttons/ToolStop.vue'
import ToolDebug from './buttons/ToolDebug.vue'
import ToolDebugContinue from './buttons/ToolDebugContinue.vue'
import ToolDebugNextStep from './buttons/ToolDebugNextStep.vue'
import ToolRecorder from './buttons/ToolRecorder.vue'
import ToolDataPick from './buttons/ToolDataPick.vue'
import ToolCustomComp from './buttons/ToolCustomComp.vue'
import ToolMultiSelect from './buttons/ToolMultiSelect.vue'
import ToolBack from './buttons/ToolBack.vue'
import ToolGroup from './buttons/ToolGroup.vue'
import ToolUnGroup from './buttons/ToolUnGroup.vue'
</script>

<template>
  <nav class="tools flex items-center justify-between bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.04] rounded-lg right-tab-close-area">
    <section class="tools-box flex items-center justify-center">
      <ProjectName>
        <template #prefix>
          <ToolBack class="!mx-0 !p-0" />
        </template>
      </ProjectName>
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <ToolUndo />
      <ToolRedo />
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <ToolMultiSelect />
      <ToolGroup />
      <ToolUnGroup />
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <ToolRecorder />
      <ToolDataPick />
      <ToolCustomComp />
    </section>
    <section class="tools-box flex items-center justify-center">
      <ToolDebug />
      <ToolDebugContinue />
      <ToolDebugNextStep />
      <ToolStop />
      <ToolRun />
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <ToolSave />
      <ToolPublish />
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
