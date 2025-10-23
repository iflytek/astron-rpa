<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Image } from 'ant-design-vue'
import { computed, ref } from 'vue'

import { getImageURL } from '@/api/http/env'
import { ATOM_FORM_TYPE } from '@/constants/atom'
import { useCvPickStore } from '@/stores/useCvPickStore'
import { useCvStore } from '@/stores/useCvStore.ts'
import { useElementsStore } from '@/stores/useElementsStore'
import { useFlowStore } from '@/stores/useFlowStore'
import { usePickStore } from '@/stores/usePickStore'
import AtomCvPopover from '@/views/Arrange/components/atomForm/AtomCvPopover.vue'
import AtomElePopover from '@/views/Arrange/components/atomForm/AtomElePopover.vue'
import { formBtnHandle } from '@/views/Arrange/components/atomForm/hooks/useRenderFormType'
import { useCvManager } from '@/views/Arrange/components/cvPick/hooks/useCvManager.ts'
import { useCvPick } from '@/views/Arrange/components/cvPick/hooks/useCvPick.ts'
import { useRenderPick } from '@/views/Arrange/components/descForm/hooks/useRenderPick'
import { ElementPickModal } from '@/views/Arrange/components/pick'
import { DEFAULT_DESC_TEXT } from '@/views/Arrange/config/flow'
import { useCreateWindow } from '@/views/Arrange/hook/useCreateWindow'

const { itemData, itemType, desc, id, canEdit } = defineProps({
  itemType: {
    type: String,
    default: '',
  },
  desc: {
    type: String,
    default: '',
  },
  itemData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
  id: {
    type: String,
    default: '',
  },
  canEdit: {
    type: Boolean,
    default: true,
  },
})

// 选择弹窗
const openModal = ref(false)
const selectValue = ref(itemData.value || [])
function changeSelect(data: Array<any>) {
  selectValue.value = data
  itemData.value = selectValue.value
  useFlowStore().setFormItemValue(itemData.key, itemData.value, id)
}
function showModal() {
  openModal.value = true
}
function handleOk() {
  // 重新拾取过程中不允许关闭弹窗
  if (useCvPickStore().isPicking)
    return
  openModal.value = false
}

function handleCancel() {
  // 重新拾取过程中不允许关闭弹窗
  if (useCvPickStore().isPicking)
    return
  openModal.value = false
}

const elementPickModal = NiceModal.useModal(ElementPickModal)
const pickLoading = ref(false)

const { PickTypeText, getPickImg, getDefaultText, getOperators } = useRenderPick()

const renderInfo = computed(() => {
  const noEmpty = desc !== DEFAULT_DESC_TEXT
  let menus = getOperators(noEmpty, itemType) || []
  menus = menus.filter((item) => {
    if (item.key === 'editPick') {
      return itemData.value[0] ? itemData.value[0].type === 'element' : false
    }
    return true
  })
  return {
    operatorsOptions: menus, // 渲染操作下拉列表
    text: noEmpty ? desc : getDefaultText(itemType), // 渲染文本
    noEmpty,
    img: noEmpty ? getPickImg(itemData, itemType) : '', // 渲染图片
  }
})

// 拾取
function pick() {
  const extra: any = { id }
  if (itemType === ATOM_FORM_TYPE.PICK) {
    extra.pickLoading = pickLoading
    extra.elementPickModal = () => elementPickModal.show()
  }
  formBtnHandle(itemData, itemType, extra)
}

// 编辑CV
function editCv(params: { id: string, name: string }) {
  const groupId = useCvStore().cvTreeData.find(item => item.elements.some(i => i.id === params.id)).id
  useCvManager().editCvItem(params, groupId)
}

// 编辑元素
function editElement(params: { id: string, name: string }) {
  const eleItem = useElementsStore().getElementById(params.id)
  if (eleItem && eleItem.commonSubType === 'batch') { // 抓取元素对象, 编辑打开数据抓取选择
    useCreateWindow().openDataPickWindow({ id: eleItem.id, noEmit: false })
    return
  }
  useElementsStore().requestElementDetail(params).then(() => {
    elementPickModal.show()
  })
}

// 重新拾取CV
function repickCv(params: { id: string, name: string }) {
  useCvStore().getCvItemDetail(params.id).then((res: any) => {
    useCvStore().setCurrentCvItem({ ...res })
    useCvPick().rePick(useCvStore().currentCvItem, true)
    pick()
  })
}

// 重新拾取元素
function repickElement(params: { id: string, name: string }) {
  const eleItem = useElementsStore().getElementById(params.id)
  if (eleItem && eleItem.commonSubType === 'batch') { // 抓取元素对象, 编辑打开数据抓取选择
    useCreateWindow().openDataPickWindow({ id: eleItem.id, noEmit: false })
    return
  }
  useElementsStore().requestElementDetail(params).then((res) => {
    const elementData = res.elementData ? JSON.parse(res.elementData) : {}
    const pickerType = elementData.picker_type || ''
    const groupName = useElementsStore().elements.find(item => item.elements.some(i => i.id === params.id)).name
    usePickStore().repick(pickerType, true, groupName, () => {})
  })
}

const editFn = {
  [ATOM_FORM_TYPE.PICK]: editElement,
  [ATOM_FORM_TYPE.CVPICK]: editCv,
}
const rePickFn = {
  [ATOM_FORM_TYPE.PICK]: repickElement,
  [ATOM_FORM_TYPE.CVPICK]: repickCv,
}

function pickClick(key: string) {
  const params = { id: itemData.value[0]?.data, name: itemData.value[0]?.value }
  switch (key) {
    case 'editPick':
      editFn[itemType](params)
      break
    case 'rePick':
      rePickFn[itemType](params)
      break
    case 'selectPick':
      showModal()
      break
    case 'pick':
      if (itemType === ATOM_FORM_TYPE.CVPICK) {
        useCvPick().pick({ groupId: '', entry: 'atomFormBtn' })
      }
      pick()
      break
    default:
      break
  }
}
</script>

<template>
  <!-- 拾取 -->
  <a-dropdown placement="bottom" :disabled="!canEdit">
    <template #overlay>
      <a-menu
        :items="renderInfo.operatorsOptions"
        @click="(item: any) => pickClick(item.key)"
      />
    </template>
    <a-tooltip placement="top" :title="renderInfo.text">
      <span class="desc-btn inline-flex items-center gap-1 text-[#2FCB64]/[.9]">
        <span class="desc-btn-text">{{ renderInfo.text }}</span>
        <template v-if="!renderInfo.noEmpty">
          <rpa-icon v-if="itemType === ATOM_FORM_TYPE.CVPICK" name="bottom-menu-img-manage" />
          <rpa-icon v-else name="bottom-menu-ele-manage" />
        </template>
        <Image v-if="renderInfo.img" class="desc-pick-img inline-block" :title="$t('fullSizeImage')" :height="14" :src="getImageURL(renderInfo.img)" />
      </span>
    </a-tooltip>
  </a-dropdown>
  <!-- 选择元素弹窗 -->
  <a-modal
    v-model:open="openModal"
    class="element-select-modal"
    :ok-text="$t('confirm')"
    :cancel-text="$t('cancel')"
    :title="`选择${PickTypeText[itemType]}`"
    :width="600"
    :z-index="10"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <AtomElePopover v-if="itemType === ATOM_FORM_TYPE.PICK" :render-data="itemData" :immediat-update="false" @select="changeSelect" />
    <AtomCvPopover v-if="itemType === ATOM_FORM_TYPE.CVPICK" :render-data="itemData" :item-chosed="selectValue[0]?.data" :show-add-btn="false" :immediat-update="false" @select="changeSelect" />
  </a-modal>
</template>

<style lang="scss" scoped>
.desc-btn {
  &-text {
    max-width: 60px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
:deep(.anticon-monitor) {
  margin-right: 0 !important;
  margin-left: 3px;
}
:deep(.ant-image) {
  display: inline-flex;
  align-items: center;
  margin-left: 5px;
}
:deep(.ant-image .desc-pick-img) {
  max-width: 50px;
  height: 14px;
  min-width: 14px;
  // margin-top: -10px;
}
:deep(.ant-image-mask-info) {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-size: 0;
  padding: 0 2px !important;
}
:deep(.ant-image .ant-image-mask .ant-image-mask-info .anticon) {
  margin-inline-end: initial;
}
:deep(.ant-image .anticon-eye) {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  color: #fff !important;
  margin: 0 !important;
  font-size: 12px !important;
}
:deep(.ant-image-mask-info > span) {
  font-size: 12px;
}
:global(.element-select-modal .atom-popover-search) {
  width: 550px !important;
}
:global(.element-select-modal .atom-popover-content) {
  width: 550px !important;
}
:global(.element-select-modal .atom-popover-footer) {
  max-width: 550px !important;
}
:global(.element-select-modal .atom-popover-inner .cv-list .cv-item) {
  margin-right: 5px;
}
:global(.element-select-modal .atom-popover-inner .cv-list .cv-item:nth-child(2n)) {
  margin-right: 5px;
}
:global(.element-select-modal .atom-popover-container) {
  display: flex;
}
:global(.element-select-modal .atom-popover-container .atom-popover-main) {
  width: 350px;
}
:global(.element-select-modal .atom-popover-container .atom-popover-search) {
  width: 350px !important;
}
:global(.element-select-modal .atom-popover-container .atom-popover-content) {
  width: 350px !important;
  height: 200px !important;
  border-radius: 4px !important;
  margin-top: 5px !important;
}
:global(.element-select-modal .atom-popover-container .atom-popover-footer) {
  width: 250px;
  max-width: 250px !important;
  height: 230px !important;
  margin-left: 10px;
  border-radius: 4px;
}
:global(.element-select-modal .atom-popover-container .element-pick) {
  display: none;
}
</style>
