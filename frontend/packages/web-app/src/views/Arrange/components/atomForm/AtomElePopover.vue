<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Empty, message } from 'ant-design-vue'
import { debounce } from 'lodash-es'
import { ref, watchEffect } from 'vue'

import { getImageURL } from '@/api/http/env'
import ElementsTree from '@/components/ElementsTree/Index.vue'
import { ATOM_FORM_TYPE, ELEMENT_IN_TYPE } from '@/constants/atom'
import { useElementsStore } from '@/stores/useElementsStore'
import type { ElementActionType, ElementsType } from '@/types/resource'
import { ElementPickModal } from '@/views/Arrange/components/pick'
import { ORIGIN_VAR } from '@/views/Arrange/config/atom'
import { useCreateWindow } from '@/views/Arrange/hook/useCreateWindow'

import { createDom, setEditTextContent } from './hooks/useAtomVarPopover'
import { formBtnHandle } from './hooks/useRenderFormType'

const { renderData, immediatUpdate } = defineProps({
  renderType: {
    type: String,
    default: '',
  },
  renderData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
  immediatUpdate: { // 选中元素时，是否立即更新表单
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['closePopover', 'select'])

const elementPickModal = NiceModal.useModal(ElementPickModal)

const { openDataPickWindow } = useCreateWindow()
const simpleImage = Empty.PRESENTED_IMAGE_SIMPLE
const collapsed = ref(true)

const useElements = useElementsStore()
const value = ref<string>('')
const searchVal = ref<string>('')
const eleImg = ref('')

const onSearch = debounce(() => {
  searchVal.value = value.value
}, 1000, {
  leading: false,
  trailing: true,
})

function handleEdit(data) {
  if (data.commonSubType === 'batch') { // 抓取元素对象, 编辑打开数据抓取选择
    openDataPickWindow({ id: data.id, noEmit: true })
    return
  }
  useElements.requestElementDetail(data).then(() => {
    elementPickModal.show()
    emit('closePopover')
  })
}

function handleDelete(data) {
  useElements.deleteElement(data).then(() => {
    message.success('删除成功')
    const { value: elementValue } = renderData
    if (!Array.isArray(elementValue))
      return
    elementValue.some((item: RPA.AtomFormItemResult) => {
      if (item.data === data.elementId) {
        setEditTextContent(renderData.key, '')
        return true
      }
      return false
    })
  })
}

function handleAction(data: { keys: ElementActionType[], data: ElementsType }) {
  const type = data.keys[0]
  if (type === 'delete') {
    handleDelete(data.data)
  }
}

function handleSelect(data: ElementsType) {
  const { name, id: elementId } = data
  useElements.setSelectedElement(data)
  emit('select', [{ type: ELEMENT_IN_TYPE, value: name, data: elementId }])
  if (immediatUpdate)
    createDom({ val: name, elementId, category: ELEMENT_IN_TYPE }, renderData, ORIGIN_VAR)
}

function handleLookOver(data: ElementsType) {
  const { imageUrl } = data
  eleImg.value = imageUrl
}

function handleNewPick() {
  const extra = {
    pickLoading: ref(true),
    elementPickModal: () => elementPickModal.show(),
  }
  formBtnHandle(renderData, ATOM_FORM_TYPE.PICK, extra)
  emit('closePopover')
}

watchEffect(() => {
  collapsed.value = renderData.value[0]?.type === ELEMENT_IN_TYPE
})
</script>

<template>
  <div class="atom-popover-container">
    <div class="atom-popover-main">
      <article class="atom-popover-header">
        <a-input
          v-model:value="value"
          class="atom-popover-search flex-1"
          :placeholder="$t('common.enter')"
          @change="onSearch"
        >
          <template #prefix>
            <rpa-icon name="search" />
          </template>
        </a-input>
        <rpa-hint-icon
          name="expand-bottom"
          :title="collapsed ? '全部收起' : '全部展开'"
          class="ml-2 h-min" :class="[collapsed ? 'rotate-180' : 'rotate-0']"
          enable-hover-bg
          @click="collapsed = !collapsed"
        />
        <rpa-hint-icon
          name="get-element-object-web"
          title="开启拾取"
          class="ml-1 element-pick"
          enable-hover-bg
          @click="handleNewPick"
        />
      </article>

      <article class="atom-popover-content">
        <ElementsTree
          :expand-all="collapsed"
          :search-val="searchVal"
          :item-chosed="renderData.value ? renderData.value[0]?.value : ''"
          parent="elementChooser"
          @edit="handleEdit"
          @delete="handleDelete"
          @selected="handleSelect"
          @look-over="handleLookOver"
          @action-click="handleAction"
        />
      </article>
    </div>
    <article class="atom-popover-footer bg-[#F3F3F7] dark:bg-[#FFFFFF]/[.08]">
      <a-image v-if="eleImg" :preview="false" :src="getImageURL(eleImg)" :height="80" />
      <a-empty v-else :image="simpleImage" :description="null" />
    </article>
  </div>
</template>

<style lang="scss" scoped>
.atom-popover-search {
  font-size: 12px;
}
.atom-popover-header {
  display: flex;
  padding-bottom: 6px;
  align-items: center;
  .pick_btn {
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

.atom-popover-content {
  width: 230px;
  height: 100px;
  overflow-y: auto;
}

.atom-popover-footer {
  max-width: 230px;
  height: 104px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.atom-popover-content::-webkit-scrollbar {
  width: 4px;
  // background: #f6f6f6;
}

.atom-popover-content::-webkit-scrollbar-thumb {
  width: 4px;
  // background: #cbcbcb;
}

:deep(.ant-tabs-nav-list > .ant-tabs-tab) {
  font-size: 12px;
}

:deep(.ant-tree-title) {
  font-size: 12px;
}
</style>
