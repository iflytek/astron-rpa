<script setup lang="ts">
import ProjectName from '../../components/projectName/Index.vue'

import ToolRedo from './buttons/ToolRedo.vue'
import ToolUndo from './buttons/ToolUndo.vue'
import ToolSave from './buttons/ToolSave.vue'
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
    </section>
    <section class="tools-box flex items-center justify-center">
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <ToolSave />
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
