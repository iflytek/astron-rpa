<script setup lang="ts">
import { Empty } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, onMounted, ref } from 'vue'

import { ELEMENT_IN_TYPE } from '@/constants/atom'
import { useCvStore } from '@/stores/useCvStore.ts'
import type { Element } from '@/types/resource'
import CvPickBtn from '@/views/Arrange/components/cvPick/CvPickBtn.vue'
import CvTree from '@/views/Arrange/components/cvPick/CvTree.vue'
import CvUploadBtn from '@/views/Arrange/components/cvPick/CvUploadBtn.vue'
import { ORIGIN_VAR } from '@/views/Arrange/config/atom'

import { createDom } from './hooks/useAtomVarPopover'

const { renderData, showAddBtn, immediatUpdate, itemChosed } = defineProps({
  renderType: {
    type: String,
    default: '',
  },
  renderData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
  showAddBtn: {
    type: Boolean,
    default: true,
  },
  immediatUpdate: {
    // 选中元素时，是否立即更新表单
    type: Boolean,
    default: true,
  },
  itemChosed: {
    // 选中元素时，是否立即更新表单
    type: String,
    default: '',
  },
})

const emit = defineEmits(['closePopover', 'select'])

const { t } = useTranslation()

const searchValue = ref<string>('')
const collapsed = ref<boolean>(true)

function toggleCollapsed() {
  collapsed.value = !collapsed.value
}

function handleSelect(data: Element) {
  const { name, id } = data
  emit('select', [{ type: ELEMENT_IN_TYPE, value: name, data: id }])
  if (immediatUpdate) {
    createDom(
      { val: name, elementId: id, category: ELEMENT_IN_TYPE },
      renderData,
      ORIGIN_VAR,
    )
  }
  emit('closePopover')
}

const cvTreeData = computed(() => {
  if (!searchValue.value)
    return useCvStore().cvTreeData
  return useCvStore()
    .cvTreeData
    .map((i) => {
      return {
        ...i,
        elements: i.elements.filter(i =>
          i.name.toLowerCase().includes(searchValue.value.toLowerCase()),
        ),
      }
    })
    .filter(i => i.elements.length > 0)
})
function closePopover() {
  emit('closePopover')
}
onMounted(() => {
  useCvStore().getCvTreeData()
})
</script>

<template>
  <div class="atom-popover-content">
    <div class="flex items-center">
      <a-input
        v-model:value="searchValue"
        class="atom-popover-search"
        :placeholder="t('searchElements')"
      />
      <rpa-hint-icon
        name="expand-bottom"
        :title="collapsed ? '全部收起' : '全部展开'"
        class="ml-[12px]"
        :class="[collapsed ? 'rotate-180' : 'rotate-0']"
        enable-hover-bg
        @click="toggleCollapsed"
      />
      <CvPickBtn v-if="showAddBtn" type="icon" enable-hover-bg />
      <CvUploadBtn v-if="showAddBtn" type="icon" enable-hover-bg />
    </div>
    <article class="atom-popover-inner">
      <CvTree
        v-if="cvTreeData.length > 0"
        item-action-type="delete"
        :tree-data="cvTreeData"
        :item-chosed="itemChosed"
        :default-collapse="!searchValue"
        :collapsed="collapsed"
        :disabled-contextmenu="true"
        :element-actions="['edit', 'delete']"
        @click="handleSelect"
        @action-click="closePopover"
      />
      <a-empty v-else :image="Empty.PRESENTED_IMAGE_SIMPLE" />
    </article>
  </div>
</template>

<style lang="scss" scoped>
.atom-popover-content {
  width: 230px;
  height: 260px;
}

.atom-popover-search {
  font-size: 12px;
}

:deep(.atom-popover-content .cv-pick-btn) {
  margin-right: 5px;
}

.atom-popover-inner {
  width: 100%;
  height: 230px;
  overflow-y: auto;
  padding-top: 10px;
  :deep(.cv-list) {
    padding: 0 8px;
  }

  :deep(.cv-list .cv-item) {
    margin-bottom: 10px;
    margin-right: 8px;
    cursor: pointer;
    border: 1px solid #eee;
    height: 106px;
    &:hover {
      background-color: #f6f6f6;
    }
  }

  :deep(.cv-list .cv-item:nth-child(2n)) {
    margin-right: 0px;
  }

  :deep(.cv-list .cv-item-img) {
    border-color: #f8f8f8;
  }

  :deep(.cv-list .pick-item-action) {
    display: block;
    right: 0;
  }
}
</style>
