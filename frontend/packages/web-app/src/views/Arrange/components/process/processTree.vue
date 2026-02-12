<script setup lang="ts">
import { ref, computed, watchPostEffect } from 'vue'
import { useTemplateRefsList } from '@vueuse/core'

import { useProcessStore } from '@/stores/useProcessStore'

import DropDownMenu from './DropdownMenu.vue'
import { ProcessActionEnum, useProcessMenuActions } from './hooks/useProcessMenus'

const refs = useTemplateRefsList<HTMLDivElement>()

const searchValue = ref<string>('')
const expand = ref(true)

const processStore = useProcessStore()

const menuList = computed(() => {
  return processStore.processList.filter(tab => tab.name.includes(searchValue.value))
})

function getCurrentProcessMenu(item: RPA.Flow.ProcessModule) {
  return useProcessMenuActions({
    item,
    disabled: () => item.isMain,
    actions: [
      ProcessActionEnum.OPEN,
      ProcessActionEnum.RENAME,
      ProcessActionEnum.COPY,
      ProcessActionEnum.SEARCH_CHILD_PROCESS,
      ProcessActionEnum.DELETE,
    ],
  })
}

async function handleClick(item: RPA.Flow.ProcessModule) {
  await processStore.saveProject()
  processStore.openProcess(item.resourceId)
}

function isActive(item: RPA.Flow.ProcessModule) {
  return item.resourceId === processStore.activeProcessId
}

watchPostEffect(() => {
  const activeIndex = menuList.value.findIndex(item => isActive(item))
  const activeElement = refs.value[activeIndex]
  activeElement?.scrollIntoView({ block: 'center', inline: 'center' })
})
</script>

<template>
  <div>
    <a-input
      v-model:value="searchValue"
      allow-clear
      class="flex-1 mb-3 leading-6"
      :placeholder="$t('common.enter')"
    >
      <template #prefix>
        <rpa-icon name="search" class="dark:text-[rgba(255,255,255,0.25)]" />
      </template>
    </a-input>
    <div class="process-tree-container">
      <div class="flex items-center gap-2 group cursor-pointer" @click="expand = !expand">
        <rpa-icon name="caret-down-small" width="16px" height="16px" class="transition-transform duration-200" :class="{ '-rotate-90': !expand }" />
        <span class="group-hover:text-primary">流程名称</span>
      </div>
      <DropDownMenu v-for="item in menuList" :key="item.resourceId" :menus="getCurrentProcessMenu(item)">
        <div
          v-show="expand"
          :ref="refs.set"
          class="flex items-center gap-1 px-1 ml-5 cursor-pointer rounded"
          :class="isActive(item) ? 'text-primary bg-[#F3F3F7] dark:bg-[#FFFFFF]/[.08]' : 'hover:text-primary hover:bg-[#F3F3F7] dark:hover:bg-[#FFFFFF]/[.08]'"
          @click="handleClick(item)"
        >
          <rpa-icon :name="item.resourceCategory === 'process' ? 'process-tree' : 'run-python-module'" width="16px" height="16px" />
          <div class="flex items-center">
            {{ item.name.slice(0, item.name.indexOf(searchValue)) }}
            <span class="text-primary font-bold">{{ searchValue }}</span>
            {{ item.name.slice(item.name.indexOf(searchValue) + searchValue.length) }}
          </div>
        </div>
      </DropDownMenu>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.process-tree-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  font-size: 12px;
  line-height: 24px;
}

.process-tree-container::-webkit-scrollbar {
  width: 4px;
}

.process-tree-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.process-tree-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.process-tree-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>