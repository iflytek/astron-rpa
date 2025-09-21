<script setup lang="ts">
import type { TreeDataItem } from 'ant-design-vue/es/tree/Tree'
import { ref, watch } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

import type { IMenuItem } from './DropdownMenu.vue'
import DropDownMenu from './DropdownMenu.vue'
import { ProcessActionEnum, useProcessMenuActions } from './hooks/useProcessMenus'

const expandedKeys = ref<string[]>([])
const searchValue = ref<string>('')
const autoExpandParent = ref<boolean>(true)
const gData = ref<TreeDataItem[]>()

const processStore = useProcessStore()

function onExpand(keys: string[]) {
  expandedKeys.value = keys
  autoExpandParent.value = false
}

watch(searchValue, (value) => {
  const expanded = dataList.map((item: TreeDataItem) => {
    if ((item.title as string).includes(value)) {
      return getParentKey(item.key as string, gData.value)
    }
    return null
  }).filter((item, i, self) => item && self.indexOf(item) === i)
  expandedKeys.value = expanded as string[]
  searchValue.value = value
  autoExpandParent.value = true
})

watch(() => processStore.changeFlag, () => {
  generateData()
})

function generateData() {
  const parent = [{ key: 'node', title: '流程名称', children: [] }]
  parent[0].children = processStore.processList.map(item => ({ title: item.name, key: item.resourceId, children: [] }))
  gData.value = parent
  expandedKeys.value = processStore.processList.map(item => item.resourceId)
}
generateData()

const dataList: TreeDataItem[] = []
function generateList(data: TreeDataItem[]) {
  for (let i = 0; i < data.length; i++) {
    const node = data[i]
    const key = node.key
    dataList.push({ key, title: node.title as string })
    if (node.children) {
      generateList(node.children)
    }
  }
}
generateList(gData.value)
expandedKeys.value = dataList.map(item => item.key as string) // 默认展开所有节点

function getParentKey(key: string, tree: TreeDataItem[]): string | number | undefined {
  let parentKey
  for (let i = 0; i < tree.length; i++) {
    const node = tree[i]
    if (node.children) {
      if (node.children.some(item => item.key === key)) {
        parentKey = node.key
      }
      else if (getParentKey(key, node.children)) {
        parentKey = getParentKey(key, node.children)
      }
    }
  }
  return parentKey
}

function handleSelect(_, { node }) {
  // 根节点key为node
  if (node.key === 'node')
    return
  // 假如点击项就是激活项，activeProcessId不会改变，ProcessHeader组件中的watch不会生效，需要手动触发滚动
  if (node.key === processStore.activeProcessId) {
    const activeProcessDom = document.getElementById(`process_${processStore.activeProcessId}`)
    activeProcessDom?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest',
    })
  }
  else {
    processStore.saveProject().then(() => {
      processStore.openProcess(node.key)
    })
  }
}

function getCurrentProcessMenu(key: string) {
  const findItem = processStore.processList.find(item => item.resourceId === key)
  if (!findItem)
    return
  const menus: IMenuItem[] = useProcessMenuActions({
    item: findItem,
    disabled: () => findItem.isMain,
    actions: [ProcessActionEnum.OPEN, ProcessActionEnum.RENAME, ProcessActionEnum.COPY, ProcessActionEnum.SEARCH_CHILD_PROCESS, ProcessActionEnum.DELETE],
  })
  return menus
}
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
      <a-tree
        :expanded-keys="expandedKeys" :auto-expand-parent="autoExpandParent" :tree-data="gData"
        @expand="onExpand"
        @select="handleSelect"
      >
        <template #title="{ title, key }">
          <DropDownMenu :menus="getCurrentProcessMenu(key)">
            <span v-if="title.includes(searchValue)" class="flex items-center">
              <rpa-icon v-if="key !== 'node'" name="process-tree" width="16px" height="16px" class="mr-1" />
              {{ title.substr(0, title.indexOf(searchValue)) }}
              <span class="text-primary font-bold">{{ searchValue }}</span>
              {{ title.substr(title.indexOf(searchValue) + searchValue.length) }}
            </span>
            <span v-else>{{ title }}</span>
          </DropDownMenu>
        </template>
      </a-tree>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.process-tree-container {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

:deep(.ant-tree) {
  font-size: 12px;
}

:deep(.ant-tree-node-content-wrapper:hover) {
  background-color: transparent;
  color: $color-primary;
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
