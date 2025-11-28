<script lang="ts" setup>
import { Empty, message } from 'ant-design-vue'
import { computed, ref, watch } from 'vue'

import ElementUseFlowList from '@/components/ElementUseFlowList/Index.vue'
import { useCvStore } from '@/stores/useCvStore.ts'
import { useProcessStore } from '@/stores/useProcessStore'
import CvTree from '@/views/Arrange/components/cvPick/CvTree.vue'
import { PICK_TYPE_CV } from '@/views/Arrange/config/atom'
import { quoteManage } from '@/views/Arrange/hook/useQuoteManage'

import type { TabContentProps } from '../../types'
import { useToolsStore } from '../../store'

const props = defineProps<TabContentProps>()

const { searchText, collapsed, moduleType, activeKey, refresh, unUseNum } = useToolsStore()

const cvStore = useCvStore()
const processStore = useProcessStore()

// 默认展示的图像数据
const cvTreeData = computed(() => {
  if (!searchText.value)
    return cvStore.cvTreeData
  return cvStore.cvTreeData.map((i) => {
    return {
      ...i,
      elements: i.elements.filter(i => i.name.toLowerCase().includes(searchText.value.toLowerCase())),
    }
  }).filter(i => i.elements.length > 0)
})

// 引用图像的流程数据
const flowItems = ref([])
// 未使用的图像数据
const unuseTreeData = ref([])

function refreshData(moduleType: string) {
  if (activeKey.value !== 'cvManagement')
    return
  switch (moduleType) {
    case 'unuse':
      cvStore.getUnUseTreeData(unuseTreeData, unUseNum, PICK_TYPE_CV)
      break
    case 'quoted':
      quoteManage(cvStore.quotedItem, list => flowItems.value = list, PICK_TYPE_CV)
      break
  }
}

watch(() => moduleType.value, (val) => {
  if (val !== 'quoted')
    useCvStore().setQuotedItem()
  refreshData(val)
})

watch(() => cvStore.cvTreeData, () => {
  if (moduleType.value === 'unuse')
    refreshData(moduleType.value)
}, { immediate: true })

watch(() => refresh.value, () => {
  if (activeKey.value !== 'cvManagement')
    return
  refreshData(moduleType.value)
  message.success('刷新成功')
})

watch(() => cvStore.quotedItem?.id, (val) => {
  if (val)
    moduleType.value = 'quoted'
})
</script>

<template>
  <div class="cv-manager" :style="{ height: `${props.height}px` }">
    <!-- 图像管理及搜索 -->
    <template v-if="moduleType === 'default'">
      <CvTree
        :storage-id="processStore.project.id"
        :tree-data="cvTreeData"
        :collapsed="!searchText && collapsed"
        :empty-text="searchText ? '未搜索到结果' : $t('noData')"
      />
    </template>
    <!-- 查看未使用元素 -->
    <template v-else-if="moduleType === 'unuse'">
      <CvTree :tree-data="unuseTreeData" :collapsed="collapsed" />
    </template>
    <!-- 查找元素引用 -->
    <template v-else-if="moduleType === 'quoted'">
      <ElementUseFlowList v-if="flowItems.length > 0" :use-name="cvStore.quotedItem?.name" :use-flow-items="flowItems" :collapsed="collapsed" />
      <a-empty v-else description="暂无引用" />
    </template>
  </div>
</template>
