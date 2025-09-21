<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { computed, ref } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import { ProcessModal } from '@/views/Arrange/components/process'

import ProcessItem from './ProcessItem.vue'

const emit = defineEmits<{ (evt: 'collapse'): void }>()

const processStore = useProcessStore()
const processModal = NiceModal.useModal(ProcessModal)

const searchValue = ref('')
const searchProcessList = computed<RPA.Flow.ProcessModule[]>(() => {
  if (!searchValue.value)
    return processStore.processList

  return processStore.processList.filter(item =>
    item.name?.includes(searchValue.value),
  )
})

const treeData = computed(() => {
  return [{
    key: 'root',
    name: '流程名称',
    children: searchProcessList.value.map(item => ({
      key: item.resourceId,
      ...item,
    })),
  }]
})

function handleSelect(_, { node: process }) {
  // 根节点没有resourceId
  if (!process.resourceId)
    return
  // 假如点击项就是激活项，activeProcessId不会改变，ProcessHeader组件中的watch不会生效，需要手动触发滚动
  if (process.resourceId === processStore.activeProcessId) {
    const activeProcessDom = document.getElementById(`process_${processStore.activeProcessId}`)
    activeProcessDom?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest',
    })
  }
  else {
    processStore.saveProject().then(() => {
      processStore.openProcess(process.resourceId)
    })
  }
}
</script>

<template>
  <div class="panel">
    <div class="flex items-center">
      <span class="text-[16px] font-semibold">流程管理</span>
      <div class="flex items-center ml-4 cursor-pointer" @click="processModal.show({ type: 'process' })">
        <rpa-icon name="close" size="16" class="mr-1 bg-[red]" />
        <span>新建流程</span>
      </div>
      <div class="flex items-center ml-4 mr-auto cursor-pointer" @click="processModal.show({ type: 'module' })">
        <rpa-icon name="close" size="16" class="mr-1 bg-[red]" />
        <span>新建Python</span>
      </div>
      <rpa-icon
        name="close"
        size="16"
        class="mr-1 cursor-pointer bg-[red]"
        @click="emit('collapse')"
      />
    </div>

    <a-input
      v-model:value="searchValue"
      :placeholder="$t('common.enter')"
      allow-clear
      :bordered="false"
      class="leading-6 bg-[#F3F3F7]"
    >
      <template #prefix>
        <rpa-icon name="search" />
      </template>
    </a-input>

    <div class="flex-1">
      <a-tree
        :tree-data="treeData"
        :field-names="{ title: 'name' }"
        block-node
        default-expand-all
        @select="handleSelect"
      >
        <template #title="item">
          <ProcessItem :process-item="item" />
        </template>
      </a-tree>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  width: 320px;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 400;
  color: rgba(0, 0, 0, 0.85);
}

:deep(.ant-tree-node-content-wrapper) {
  overflow: hidden;
}
</style>
