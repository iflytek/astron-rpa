<script lang="ts" setup>
import { Empty, message } from 'ant-design-vue'
import { computed, inject, ref, watch } from 'vue'
import type { Ref } from 'vue'

import ElementUseFlowList from '@/components/ElementUseFlowList/Index.vue'
import { useCvStore } from '@/stores/useCvStore.ts'
import { useProcessStore } from '@/stores/useProcessStore'
import CvTree from '@/views/Arrange/components/cvPick/CvTree.vue'
import { PICK_TYPE_CV } from '@/views/Arrange/config/atom'
import { quoteManage } from '@/views/Arrange/hook/useQuoteManage'

defineProps({
  operates: {
    type: Object,
  },
})

const collapsed = inject<Ref<boolean>>('collapsed')
const searchText = inject<Ref<string>>('searchText')
const moduleType = inject<Ref<string>>('moduleType')
const refresh = inject<Ref<boolean>>('refresh')
const unUseNum = inject<Ref<number>>('unUseNum')
const activeTab = inject<Ref<string>>('activeTab')
const height = inject<Ref<number>>('logTableHeight', ref(180))

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
  if (activeTab.value !== 'cvManagement')
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
  if (activeTab.value !== 'cvManagement')
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
  <div class="cv-manager" :style="{ height: `${height}px` }">
    <!-- 图像管理及搜索 -->
    <template v-if="moduleType === 'default'">
      <CvTree v-if="cvTreeData.length > 0" :storage-id="processStore.project.id" :tree-data="cvTreeData" :default-collapse="!searchText" :collapsed="collapsed" />
      <a-empty v-else :image="Empty.PRESENTED_IMAGE_SIMPLE" :description="searchText ? '未搜索到结果' : $t('noData')" />
    </template>
    <!-- 查看未使用元素 -->
    <template v-else-if="moduleType === 'unuse'">
      <CvTree v-if="unuseTreeData.length > 0" :tree-data="unuseTreeData" :default-collapse="false" :collapsed="collapsed" />
      <a-empty v-else description="暂无未使用元素" />
    </template>
    <!-- 查找元素引用 -->
    <template v-else-if="moduleType === 'quoted'">
      <ElementUseFlowList v-if="flowItems.length > 0" :use-name="cvStore.quotedItem?.name" :use-flow-items="flowItems" :collapsed="collapsed" />
      <a-empty v-else description="暂无引用" />
    </template>
  </div>
</template>
