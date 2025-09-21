<script lang="ts" setup>
import {
  ArrowRightOutlined,
  CaretDownOutlined,
  CaretRightOutlined,
} from '@ant-design/icons-vue'
import { computed, nextTick, ref, watch } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import type { PickUseItemType } from '@/types/resource.d'
import { clickAtom } from '@/views/Arrange/components/flow/hooks/useFlow'
import ItemDesc from '@/views/Arrange/components/flow/ItemDesc.vue'
import ItemTitle from '@/views/Arrange/components/flow/ItemTitle.vue'
import { atomScrollIntoView } from '@/views/Arrange/utils'

const { useName, useFlowItems, collapsed } = defineProps({
  useName: {
    // 引用的图像名称
    type: String,
    default: '',
  },
  useFlowItems: {
    type: Array<PickUseItemType>,
    default: () => [],
  },
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const processStore = useProcessStore()

const useLength = computed(() => {
  let length = 0
  useFlowItems.forEach((item) => {
    length += item.atoms.length
  })
  return length
})

// 展开折叠
const openKeys = ref([])
function toggleOpen(key: string, flag: boolean) {
  if (flag) {
    openKeys.value.push(key)
  }
  else {
    openKeys.value = openKeys.value.filter(i => i !== key)
  }
}

watch(() => useFlowItems, (val) => {
  openKeys.value = val.map(i => i.processId)
}, { immediate: true })

// 全部展开/折叠
watch(() => collapsed, (val) => {
  openKeys.value = !val ? useFlowItems.map(i => i.processId) : []
})

function skipFlowAtom(processId: string, atomId: string) {
  processStore.activeProcessId !== processId && processStore.checkActiveProcess(processId)
  clickAtom(({ ctrlKey: false, shiftKey: false } as MouseEvent), {
    id: atomId,
    key: '',
    icon: '',
    title: '',
    level: 1,
    version: '',
    alias: '',
    advanced: [],
    exception: [],
    inputList: [],
    outputList: [],
  })
  nextTick(() => atomScrollIntoView(atomId))
}
</script>

<template>
  <div class="cv-use">
    <div class="cv-use-header bg-[#D7D7FF]/[.4] dark:bg-[#5D59FF]/[.35] rounded">
      <rpa-hint-icon name="open-folder" />
      <span class="mx-1">{{ useName }}</span>
      <span>({{ useLength }})</span>
    </div>
    <div v-for="item in useFlowItems" class="cv-use-flow-item">
      <div class="h-[28px] flex items-center select-none">
        <span class="cursor-pointer mr-1" @click="toggleOpen(item.processId, !openKeys.includes(item.processId))">
          <CaretDownOutlined v-if="openKeys.includes(item.processId)" />
          <CaretRightOutlined v-else />
        </span>
        <rpa-icon name="process-tree" size="16" />
        <span class="mx-1">{{ item.processName }}</span>
        <span>({{ item.atoms.length }})</span>
      </div>
      <template v-if="openKeys.includes(item.processId)">
        <div
          v-for="atom in item.atoms"
          class="cv-use-flow-atom h-[28px] flex items-center"
          @dblclick="skipFlowAtom(item.processId, atom.id)"
        >
          <span class="cursor-pointer text-primary" @click="skipFlowAtom(item.processId, atom.id)">
            第{{ atom.index }}行
            <ArrowRightOutlined />
          </span>
          <ItemTitle :item="atom" :show-validate="false" />
          <ItemDesc :item="atom" :can-edit="false" :flow-id="item.processId" />
        </div>
      </template>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.cv-use {
  &-header {
    height: 28px;
    display: flex;
    align-items: center;
    font-size: 12px;
    padding-left: 10px;
  }

  &-flow {
    &-item {
      padding: 5px 10px;
      font-size: 12px;
    }

    &-atom {
      padding-left: 30px;
      line-height: 24px;

      :deep(.desc) {
        word-break: break-all;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 1;
        overflow: hidden;
        line-height: 1.5;
        // color: #888;
        padding-left: 10px;
        flex: 1;
      }

      :deep(.desc-edit-text) {
        display: inline;
      }

      :deep(.comment-variable) {
        color: #2c69ff;
        background: #ecf0ff;
        border-radius: 3px;
        display: inline-flex;
        padding: 0 2px;
        max-width: 200px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      &-row {
        color: #4e68f6;
      }

      :deep(.anticon-arrow-right) {
        margin: 0 5px 0 3px;
      }
    }
  }
}
</style>
