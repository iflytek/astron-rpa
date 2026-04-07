<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Image } from 'ant-design-vue'
import { computed, ref } from 'vue'

import { getImageURL } from '@/api/http/env'
import { ATOM_FORM_TYPE } from '@/constants/atom'
import { useCvPickStore } from '@/stores/useCvPickStore'
import { useCvStore } from '@/stores/useCvStore'
import { useElementsStore } from '@/stores/useElementsStore'
import { usePickStore } from '@/stores/usePickStore'
import CvPopover from '@/views/Arrange/components/cvPick/CvPopover.vue'
import ElePopover from '@/views/Arrange/components/pick/ElePopover.vue'
import { useCvManager } from '@/views/Arrange/components/cvPick/hooks/useCvManager'
import { useCvPick } from '@/views/Arrange/components/cvPick/hooks/useCvPick'
import { useRenderPick } from '@/views/Arrange/components/flow/descForm/hooks/useRenderPick'
import { ElementPickModal } from '@/views/Arrange/components/pick'
import { DEFAULT_DESC_TEXT } from '@/views/Arrange/config/flow'
import { useCreateWindow } from '@/views/Arrange/hook/useCreateWindow'

interface Props {
  itemType: ATOM_FORM_TYPE.PICK | ATOM_FORM_TYPE.CVPICK
  desc: string
  itemData: RPA.AtomDisplayItem
  id: string
  canEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canEdit: true,
})

// 选择弹窗相关
const openModal = ref(false)
const selectValue = ref<RPA.AtomFormItemResult[]>(
  Array.isArray(props.itemData.value) ? props.itemData.value : []
)

const elementPickModal = NiceModal.useModal(ElementPickModal)
const pickLoading = ref(false)

const { PickTypeText, getPickImg, getDefaultText, getOperators } = useRenderPick()

/**
 * 处理选择变化
 */
function changeSelect(data: RPA.AtomFormItemResult[]) {
  selectValue.value = data
  props.itemData.value = selectValue.value
}

/**
 * 显示选择弹窗
 */
function showModal() {
  openModal.value = true
}

/**
 * 关闭弹窗（拾取过程中不允许关闭）
 */
function closeModal() {
  if (useCvPickStore().isPicking) {
    return
  }
  openModal.value = false
}

/**
 * 渲染信息计算属性
 */
const renderInfo = computed(() => {
  const noEmpty = props.desc !== DEFAULT_DESC_TEXT
  const operators = getOperators(noEmpty, props.itemType) || []
  
  // 过滤操作选项：编辑操作仅在元素类型时显示
  const filteredOperators = operators.filter((item) => {
    if (item.key === 'editPick') {
      return props.itemData.value?.[0]?.type === 'element'
    }
    return true
  })

  return {
    operatorsOptions: filteredOperators,
    text: noEmpty ? props.desc : getDefaultText(props.itemType),
    noEmpty,
    img: noEmpty ? getPickImg(props.itemData, props.itemType) : '',
  }
})

/**
 * 处理元素批量类型
 */
function handleBatchElement(elementId: string) {
  useCreateWindow().openDataPickWindow({ id: elementId, noEmit: false })
}

/**
 * 拾取操作
 */
function pick() {
  const extra: Record<string, any> = { id: props.id }
  if (props.itemType === ATOM_FORM_TYPE.PICK) {
    extra.pickLoading = pickLoading
    extra.elementPickModal = () => elementPickModal.show()
  }
}

/**
 * 编辑CV
 */
function editCv(params: { id: string; name: string }) {
  const cvStore = useCvStore()
  const groupId = cvStore.cvTreeData.find(
    item => item.elements.some(i => i.id === params.id)
  )?.id
  
  if (groupId) {
    useCvManager().editCvItem(params, groupId)
  }
}

/**
 * 编辑元素
 */
function editElement(params: { id: string; name: string }) {
  const elementsStore = useElementsStore()
  const eleItem = elementsStore.getElementById(params.id)
  
  if (eleItem?.commonSubType === 'batch') {
    handleBatchElement(eleItem.id)
    return
  }
  
  elementsStore.requestElementDetail(params).then(() => {
    elementPickModal.show()
  })
}

/**
 * 重新拾取CV
 */
function repickCv(params: { id: string; name: string }) {
  const cvStore = useCvStore()
  cvStore.getCvItemDetail(params.id).then((res: any) => {
    cvStore.setCurrentCvItem({ ...res })
    useCvPick().rePick(cvStore.currentCvItem, true)
    pick()
  })
}

/**
 * 重新拾取元素
 */
function repickElement(params: { id: string; name: string }) {
  const elementsStore = useElementsStore()
  const eleItem = elementsStore.getElementById(params.id)
  
  if (eleItem?.commonSubType === 'batch') {
    handleBatchElement(eleItem.id)
    return
  }
  
  elementsStore.requestElementDetail(params).then((res) => {
    const elementData = res.elementData ? JSON.parse(res.elementData) : {}
    const pickerType = elementData.picker_type || ''
    const groupName = elementsStore.elements.find(
      item => item.elements.some(i => i.id === params.id)
    )?.name
    
    if (groupName) {
      usePickStore().repick(pickerType, true, groupName, () => {})
    }
  })
}

// 操作函数映射
const editFnMap = {
  [ATOM_FORM_TYPE.PICK]: editElement,
  [ATOM_FORM_TYPE.CVPICK]: editCv,
} as const

const rePickFnMap = {
  [ATOM_FORM_TYPE.PICK]: repickElement,
  [ATOM_FORM_TYPE.CVPICK]: repickCv,
} as const

/**
 * 处理拾取操作点击
 */
function pickClick(key: string) {
  const firstValue = props.itemData.value?.[0]
  if (!firstValue) {
    return
  }

  const params = { id: firstValue.data, name: firstValue.value }

  switch (key) {
    case 'editPick':
      editFnMap[props.itemType]?.(params)
      break
    case 'rePick':
      rePickFnMap[props.itemType]?.(params)
      break
    case 'selectPick':
      showModal()
      break
    case 'pick':
      if (props.itemType === ATOM_FORM_TYPE.CVPICK) {
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
  <a-dropdown placement="bottom" :disabled="!props.canEdit">
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
          <rpa-icon v-if="props.itemType === ATOM_FORM_TYPE.CVPICK" name="bottom-menu-img-manage" />
          <rpa-icon v-else name="bottom-menu-ele-manage" />
        </template>
        <Image
          v-if="renderInfo.img"
          class="desc-pick-img inline-block"
          :title="$t('fullSizeImage')"
          :height="14"
          :src="getImageURL(renderInfo.img)"
        />
      </span>
    </a-tooltip>
  </a-dropdown>
  <!-- 选择元素弹窗 -->
  <a-modal
    v-model:open="openModal"
    class="element-select-modal"
    :ok-text="$t('confirm')"
    :cancel-text="$t('cancel')"
    :title="`选择${PickTypeText[props.itemType]}`"
    :width="600"
    :z-index="10"
    @ok="closeModal"
    @cancel="closeModal"
  >
    <ElePopover
      v-if="props.itemType === ATOM_FORM_TYPE.PICK"
      :render-data="props.itemData"
      @select="changeSelect"
    />
    <CvPopover
      v-if="props.itemType === ATOM_FORM_TYPE.CVPICK"
      :render-data="props.itemData"
      :item-chosed="selectValue[0]?.data"
      :show-add-btn="false"
      @select="changeSelect"
    />
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
