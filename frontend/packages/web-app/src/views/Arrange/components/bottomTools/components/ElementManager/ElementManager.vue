<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { Image, message } from 'ant-design-vue'
import type { Ref } from 'vue'
import { computed, inject, ref, watch } from 'vue'

import { getImageURL } from '@/api/http/env'
import ElementsTree from '@/components/ElementsTree/Index.vue'
import ElementUseFlowList from '@/components/ElementUseFlowList/Index.vue'
import { clipboardManager } from '@/platform'
import { useElementsStore } from '@/stores/useElementsStore'
import { usePickStore } from '@/stores/usePickStore'
import { useProcessStore } from '@/stores/useProcessStore'
import type { ElementActionType, ElementsType, GroupContextMenuType } from '@/types/resource.d'
import { ElementPickModal } from '@/views/Arrange/components/pick'
import { useCreateWindow } from '@/views/Arrange/hook/useCreateWindow'
import { quoteManage } from '@/views/Arrange/hook/useQuoteManage'

import { useGroupManager } from '../hooks/useGroup'

const searchText = inject<Ref<string>>('searchText')
const collapsed = inject<Ref<boolean>>('collapsed')
const moduleType = inject<Ref<string>>('moduleType')
const activeTab = inject<Ref<string>>('activeTab')
const height = inject<Ref<number>>('logTableHeight', ref(180)) // 若没有注入，默认值为320

const refresh = inject<Ref<boolean>>('refresh')
const useElements = useElementsStore()
const usePick = usePickStore()
const useGroup = useGroupManager()
const processStore = useProcessStore()
const { openDataPickWindow } = useCreateWindow()
const flowItems = ref([])
const currentItem = ref()

const expandTreeAll = computed(() => collapsed.value)
const checkUnused = computed(() => activeTab.value === 'elements' && moduleType.value === 'unuse')

watch(() => refresh.value, () => {
  if (activeTab.value !== 'elements')
    return

  quoteManage(currentItem.value, list => flowItems.value = list)
  message.success('刷新成功')
})
function handleRename(data) {
  useElements.renameElement(data).then(() => {
    console.log('rename success')
  })
}

function handleRePick(data) {
  if (data.commonSubType === 'batch') { // 抓取元素对象, 编辑打开数据抓取选择
    openDataPickWindow({ id: data.id, noEmit: true })
    return
  }
  useElements.requestElementDetail(data).then((res) => {
    const elementData = res.elementData ? JSON.parse(res.elementData) : {}
    const pickerType = elementData.picker_type || ''
    const type = pickerType === 'ELEMENT' ? 'ELEMENT' : pickerType
    const groupName = data.groupName
    usePick.repick(type, true, groupName, () => {
      console.log('repick success')
    })
  })
}

function handleEdit(data) {
  if (data.commonSubType === 'batch') { // 抓取元素对象, 编辑打开数据抓取选择
    openDataPickWindow({ id: data.id, noEmit: true })
    return
  }
  useElements.requestElementDetail(data).then(() => {
    NiceModal.show(ElementPickModal)
  })
}

function handleDelete(data: ElementsType) {
  useElements.deleteElement(data).then(() => {
    console.log('delete success')
    message.success('删除成功')
  })
}

function handleSelect(data) {
  console.log('选择的', data)
  useElements.setSelectedElement(data)
}

function handleContextMenu(data: { key: GroupContextMenuType, data: ElementsType }) {
  console.log('handleContextMenu data: ', data)
  if (data.key === 'elementPick') {
    const group = data.data.name
    usePick.groupPick('', group, () => {
      console.log('groupPick success')
    })
  }
  if (data.key === 'delete') {
    useGroup.delGroup(data.data, 'common')
  }
  if (data.key === 'rename') {
    useGroup.renameGroup(data.data, 'common')
  }
}

function handleAction(data: { keys: ElementActionType[], data: ElementsType }) {
  const type = data.keys[0]

  if (type === 'delete') {
    handleDelete(data.data)
  }
  else if (type === 'edit') {
    handleEdit(data.data)
  }
  else if (type === 'repick') {
    handleRePick(data.data)
  }
  else if (type === 'move') {
    if (data.data.groupId === data.keys[1])
      return
    useGroup.move2Group(data.data.id, data.keys[1], 'common')
  }
  else if (type === 'copy') {
    useElements.elementCopy(data.data.id)
  }
  else if (type === 'copy-references') {
    clipboardManager.writeClipboardText(`${data.data.name} = WinPick(h.element("${data.data.id}"))`)
    message.success('复制成功')
  }
  else if (data.keys[0] === 'quoted') {
    moduleType.value = 'quoted'
    currentItem.value = data.data
    quoteManage(data.data, list => flowItems.value = list)
  }
}
</script>

<template>
  <div class="elements-manager">
    <div class="elements-manager__container flex ">
      <div class="elements-manager__tree flex-1 " :style="`height: ${height}px;`">
        <template v-if="moduleType === 'quoted'">
          <ElementUseFlowList v-if="flowItems.length > 0" :use-name="currentItem?.name" :use-flow-items="flowItems" :collapsed="collapsed" />
          <a-empty v-else description="暂无引用" />
        </template>
        <ElementsTree
          v-else
          :storage-id="processStore.project.id"
          :expand-all="expandTreeAll"
          :search-val="searchText"
          :check-unused="checkUnused"
          :disabled-contextmenu="false"
          @edit="handleEdit"
          @delete="handleDelete"
          @selected="handleSelect"
          @rename="handleRename"
          @repick="handleRePick"
          @contextmenu="handleContextMenu"
          @action-click="handleAction"
        />
      </div>
      <div class="elements-manager__content">
        <div class="postElement-content_pickNew">
          <div class="pickBut">
            <span class="element-title">{{ useElements.selectedElement.name }}</span>
            <!-- <div class="pickBut-btns normal">
              <a-button :loading="defaultPickLoading" size="small" :disabled="pickBtnDisabled" :icon="h(PlusOutlined)" type="link" @click="pickNew">
                {{ $t("pickupNewElement") }}
              </a-button>
            </div>
            <div class="pickBut-btns cv">
              <a-button :loading="cvPickLoading" size="small" :disabled="pickBtnDisabled || true" :icon="h(PlusOutlined)" type="link" @click="pickCV">
                {{ $t("cvPickup") }}
              </a-button>
            </div> -->
          </div>
          <div class="preview dark:bg-[rgba(255,255,255,0.08)] bg-[#f3f3f7]">
            <div class="pick-img">
              <Image v-if="useElements.selectedElement.imageUrl" :title="$t('fullSizeImage')" :src="getImageURL(useElements.selectedElement.imageUrl)" alt="元素图片" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.elements-manager__tree {
  // height: 180px;
  overflow: hidden;
  padding: 8px;
  overflow-y: auto;
}

.elements-manager__tree::-webkit-scrollbar {
  width: 4px;
  background: #f6f6f6;
}

.elements-manager__tree::-webkit-scrollbar-thumb {
  width: 4px;
  background: #cbcbcb;
}

.postElement-content_pickNew {
  width: 236px;
  margin: 0 8px 16px 8px;
  display: flex;
  flex-direction: column;

  .pickBut {
    width: 100%;
    font-size: 12px;
    height: 35px;
    line-height: 35px;
    margin-bottom: 5px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;

    .element-title {
      display: inline-block;
      text-overflow: ellipsis;
      width: 100%;
      overflow: hidden;
      white-space: nowrap;
    }

    .pickIcon {
      color: $color-primary;
      margin-right: 10px;
    }

    .pickBut-btns {
      width: 48%;
      height: 35px;
      line-height: 35px;
      border-radius: 2px;
      border: 1px solid #e7e8ec;
      text-align: center;
      display: inline-flex;
      justify-content: center;
    }
  }

  .preview {
    width: 100%;
    border-radius: 2px;
    height: 138px;

    .pick-img {
      width: 100%;
      height: 138px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

:deep(.pickBut .ant-btn) {
  height: 35px;
  line-height: 35px;
  display: flex;
  align-items: center;
  font-size: 12px;
}
:deep(.pick-img .ant-image .ant-image-img) {
  // max-width: 100%;
  width: auto;
  height: auto;
  max-height: 100px;
  max-width: 150px;
}
:deep(.ant-image-preview-operations) {
  background: rgb(0 0 0 / 44%);
}
:deep(.ant-image-preview-root .ant-image-preview-mask) {
  background: rgb(255 255 255);
}
:deep(.pick-img .ant-image) {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

:deep(.ant-tree) {
  background: transparent !important;
}

:deep(.ant-tree-switcher-icon) {
  svg {
    vertical-align: middle !important; // 树节点展开折叠图标垂直居中
  }
}
</style>
