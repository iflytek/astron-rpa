<!-- 元素编辑器 -->
<script lang="ts" setup>
import {
  BorderOuterOutlined,
  CheckCircleOutlined,
  CloseOutlined,
  RedoOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Image, message } from 'ant-design-vue'
import { throttle } from 'lodash-es'
import { h, ref, toRaw, watch } from 'vue'

import { isBase64Image, trimBase64Header } from '@/utils/common'

import { getImageURL } from '@/api/http/env'
import { useElementsStore } from '@/stores/useElementsStore'
import { usePickStore } from '@/stores/usePickStore'
import type { PickElementType } from '@/types/resource.d'
import {
  CUSTOM_OPTIONS,
  CUSTOMIZATION,
  MATCH_OPTIONS,
  VISUALIZATION,
} from '@/views/Arrange/config/pick'
import {
  elementCustomFormat,
  elementCustomFormatRecover,
  elementDirectoryFormat,
  elementDirectoryFormatRecover,
} from '@/views/Arrange/utils/elementsUtils'

import CustomTable from './CustomTable.vue'
import DirectoryTable from './DirectoryTable.vue'
import PickForm from './PickForm.vue'

defineProps({
  isContinue: {
    type: Boolean,
    default: false,
  },
})

const modal = NiceModal.useModal()
const loading = ref('')
const singleLoading = ref('') // 某个按钮loading状态
const useElements = useElementsStore()
const usePick = usePickStore()

const pickerType = ref('') // 拾取类型
const similarButton = ref(false) // 是否可以拾取相似元素
const similarCount = ref(0) // 相似元素数量
const formOption = ref({
  pickName: '', // 拾取元素名称
  editXPathType: VISUALIZATION, // xpath类型，可视化/自定义/ 单选
  customOptions: CUSTOM_OPTIONS, // 编辑类型[可视化/自定义]
  matchTypes: [], // 匹配类型 多选
  matchOptions: MATCH_OPTIONS, // 匹配方式
  pickType: 'web', // 拾取类型
})
const pickFormRef = ref() // 表单ref
const customData = ref([]) // 自定义数据
const nodeSourceData = ref([]) // 可视化数据
const detailElementData = ref<PickElementType>({
  // 元素详情
  app: '',
  version: '',
  type: 'uia',
  path: null,
})
const isShadow = ref(false) // 是否是阴影元素

/**
 * 取消
 */
function handleCancel() {
  // 重新拾取过程中不允许关闭弹窗
  if (usePick.isPicking)
    return

  modal.hide()
  useElements.resetCurrentElement()
}

/**
 * 获取当前元素最新数据
 * 处理部分数据格式
 */
function getLatestCurrentElementData(isSave: boolean) {
  const { version, type } = detailElementData.value
  let elementPathData
  let elementData
  if (type === 'web') {
    const customDataMap = toRaw(
      elementCustomFormatRecover(version, type, customData.value),
    ) // url, xpath, cssSelector
    const pathDirs = toRaw(
      elementDirectoryFormatRecover(version, type, nodeSourceData.value),
    ) // pathDirs
    elementPathData = {
      ...detailElementData.value.path,
      ...customDataMap,
      pathDirs,
      checkType: formOption.value.editXPathType,
      matchTypes: formOption.value.matchTypes,
    }
    if (isSave) {
      // 删除掉不需要的数据
      'img' in detailElementData.value && delete detailElementData.value.img
      'similarCount' in elementPathData && delete elementPathData.similarCount
      'rect' in elementPathData && delete elementPathData.rect
    }
    elementData = {
      ...detailElementData.value, // 元素外层数据
      path: elementPathData, // 元素路径数据
    }
  }
  else {
    elementPathData = elementDirectoryFormatRecover(
      version,
      type,
      nodeSourceData.value,
    ) // path 数据
    const selfImg = useElements.currentElement.imageUrl
    const parentImg = useElements.currentElement.parentImageUrl
    // 保存时若是base64图片，则不保存base64
    const img = isSave
      ? {
          self: isBase64Image(selfImg) ? '' : selfImg,
          parent: isBase64Image(parentImg) ? '' : parentImg,
        }
      : {
          self: isBase64Image(selfImg) ? trimBase64Header(selfImg) : selfImg,
          parent: isBase64Image(parentImg)
            ? trimBase64Header(parentImg)
            : parentImg,
        }
    elementData = {
      ...detailElementData.value, // 元素数据
      img,
      path: elementPathData,
    }
    if (elementData.picker_type === 'SIMILAR') {
      // uia 相似度元素，保存时变更 字段
      elementData.img = {
        self: isBase64Image(selfImg) ? '' : selfImg,
        parent: isBase64Image(parentImg) ? '' : parentImg,
      }
      elementData.similar_count ? delete elementData.similar_count : ''
    }
  }
  return elementData
}
/**
 * 继续拾取
 */
function pickContinue() {
  usePick.newPick('', () => {
    loading.value = ''
  })
}
function saveBtnLoading(btn: string) {
  return loading.value === btn
}
function saveBtnDisabled() {
  return loading.value !== '' || usePick.isPicking || usePick.isChecking
}

/**
 * 保存元素
 */
const handleOk = throttle(
  async (saveContinue: boolean) => {
    const valid = await pickFormRef.value.validateName()
    if (!valid)
      return

    const elementData = getLatestCurrentElementData(true)
    const name = formOption.value.pickName.trim()
    if (name === '') {
      message.error('请输入元素名称')
      return
    }

    if (useElements.checkName(name, useElements.currentElement.id)) {
      message.error('元素名称不可重名')
      return
    }

    loading.value = saveContinue ? 'save_continue' : 'save'
    await useElements.saveElement(elementData, name, !saveContinue)
    loading.value = ''

    modal.hide()
    useElements.resetCurrentElement()
    // 继续开启拾取
    saveContinue && pickContinue()
  },
  1500,
  { leading: true, trailing: false },
)

/**
 * 校验元素
 */
const handleValidateElement = throttle(
  () => {
    const elementData = getLatestCurrentElementData(false)
    console.log('校验 elementData: ', elementData)
    const element = JSON.stringify(elementData)
    usePick.startCheck(pickerType.value, element, (res) => {
      if (res.success)
        message.success('校验成功')
    })
  },
  1500,
  { leading: true, trailing: false },
)

/**
 * 重新拾取
 */
const rePick = throttle(
  () => {
    singleLoading.value = 'rePick'
    const type = pickerType.value === 'SIMILAR' ? 'ELEMENT' : pickerType.value // 相似元素重新拾取，需要切换为 ELEMENT
    usePick.repick(type, false, '', () => {
      singleLoading.value = ''
    }) // 无需弹窗
  },
  1500,
  { leading: true, trailing: false },
)
/**
 * 相似元素拾取
 */
const similarPick = throttle(
  () => {
    singleLoading.value = 'similarPick'
    const elementData = getLatestCurrentElementData(false)
    usePick.similarPick(elementData, () => {
      singleLoading.value = ''
    })
  },
  1500,
  { leading: true, trailing: false },
)

// 监听  useElements.currentElement 的变化更新展示
watch(
  () => useElements.currentElement,
  (newVal) => {
    if (newVal.elementData) {
      const eleData = JSON.parse(newVal.elementData)
      // console.log('eleData: ', eleData)
      const { version, type, path, picker_type, similar_count } = eleData
      // 当前元素名称
      formOption.value.pickName = newVal.name
      // 当前元素数据
      detailElementData.value = eleData
      // 拾取类型
      pickerType.value = picker_type
      // 自定义编辑元素
      customData.value = elementCustomFormat(version, type, path)
      // 设置相似拾取按钮展示
      similarButton.value = ['web', 'uia'].includes(type)
      formOption.value.pickType = type
      // 若是相似元素，获取到相似元素个数
      if (type === 'web') {
        const { checkType, matchTypes, shadowRoot } = path
        // 相似元素个数
        similarCount.value = path.similarCount ? path.similarCount : 0 // 设置相似元素个数
        // 设置元素展示类型, shadowRoot 为 true 时，展示自定义
        formOption.value.editXPathType = checkType || VISUALIZATION
        formOption.value.editXPathType = shadowRoot
          ? CUSTOMIZATION
          : formOption.value.editXPathType
        isShadow.value = shadowRoot
        formOption.value.customOptions = shadowRoot
          ? CUSTOM_OPTIONS.filter(item => item.value === CUSTOMIZATION)
          : CUSTOM_OPTIONS
        // 设置元素匹配类型
        formOption.value.matchTypes = matchTypes || []
      }
      else if (type === 'uia') {
        similarCount.value = picker_type === 'SIMILAR' ? similar_count : 0 // 设置相似元素个数
        formOption.value.customOptions = CUSTOM_OPTIONS.filter(
          item => item.value === VISUALIZATION,
        )
      }
      else {
        formOption.value.customOptions = CUSTOM_OPTIONS.filter(
          item => item.value === VISUALIZATION,
        )
      }
      // 可视化编辑元素
      nodeSourceData.value = elementDirectoryFormat(version, type, path)
    }
  },
  { immediate: true, deep: true },
)
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    destroy-on-close
    centered
    :width="730"
    :z-index="10"
    :title="$t('elementPicking')"
    class="pickModal"
    :keyboard="false"
    :mask-closable="false"
  >
    <template #closeIcon>
      <CloseOutlined
        :class="saveBtnDisabled() ? 'not-allowed' : ''"
        @click.stop="handleCancel"
      />
    </template>
    <template #footer>
      <a-button key="back" :disabled="saveBtnDisabled()" @click="handleCancel">
        {{ $t("cancel") }}
      </a-button>
      <a-button
        v-if="isContinue"
        key="save_continue"
        type="primary"
        :loading="saveBtnLoading('save_continue')"
        :disabled="saveBtnDisabled()"
        @click="
          () => {
            handleOk(true);
          }
        "
      >
        {{ $t("saveAndContinue") }}
      </a-button>
      <a-button
        key="save"
        type="primary"
        :loading="saveBtnLoading('save')"
        :disabled="saveBtnDisabled()"
        @click="handleOk(false)"
      >
        {{ $t("done") }}
      </a-button>
    </template>
    <div class="pickWrapper">
      <a-row class="pickWrapper-option">
        <a-col :span="5">
          <div
            class="pickWrapper-img border border-border mt-4 flex justify-center align-center"
          >
            <Image
              v-if="useElements.currentElement.imageUrl"
              :title="$t('fullSizeImage')"
              :src="getImageURL(useElements.currentElement.imageUrl)"
            />
          </div>
        </a-col>
        <a-col :span="6" class="pl-2">
          <div class="pickWrapper-buttons mt-4">
            <a-button
              size="small"
              :icon="h(RedoOutlined)"
              :loading="singleLoading === 'rePick' && usePick.isPicking"
              :disabled="usePick.isPicking || usePick.isChecking"
              class="font-size-12 inline-flex-center"
              @click="rePick"
            >
              {{ $t("rePickupElement") }}
            </a-button>
          </div>
          <div class="pickWrapper-buttons mt-2">
            <a-button
              class="font-size-12 inline-flex-center"
              :icon="h(BorderOuterOutlined)"
              size="small"
              :loading="usePick.isChecking"
              :disabled="usePick.isPicking"
              @click="handleValidateElement"
            >
              {{ $t("validateElement") }}
            </a-button>
          </div>
          <div class="pickWrapper-buttons mt-2">
            <a-button
              v-if="similarButton"
              size="small"
              :icon="h(UnorderedListOutlined)"
              :loading="singleLoading === 'similarPick' && usePick.isPicking"
              :disabled="usePick.isPicking || usePick.isChecking"
              class="font-size-12 inline-flex-center"
              @click="similarPick"
            >
              {{ $t("similarElementsPickup") }}
            </a-button>
          </div>
          <div v-if="similarCount" class="mt-1">
            <span class="similar-counts"><CheckCircleOutlined
              class="mr-2"
              style="color: #52c41a"
            />已找到{{ similarCount }}个相似元素</span>
          </div>
        </a-col>
        <a-col :span="13">
          <div class="pickWrapper-form mt-4">
            <PickForm ref="pickFormRef" :form-option="formOption" />
          </div>
        </a-col>
      </a-row>
      <div class="pickWrapper-table border-t border-b border-border mt-4">
        <div class="table-wapper">
          <div
            v-if="formOption.editXPathType === CUSTOMIZATION"
            :key="CUSTOMIZATION"
            class="px-2 fade-in"
          >
            <CustomTable :custom-data="customData" />
          </div>
          <div
            v-if="formOption.editXPathType === VISUALIZATION && !isShadow"
            :key="VISUALIZATION"
            class="px-2 fade-in"
          >
            <DirectoryTable :node-source="nodeSourceData" />
          </div>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<style scoped lang="scss">
.font-size-12 {
  font-size: 12px;
}
.inline-flex-center {
  display: inline-flex;
  align-items: center;
}

.pickWrapper-table {
  height: 230px;
  overflow-y: auto;
}

.pickWrapper-table::-webkit-scrollbar {
  width: 6px;
  background-color: #f5f5f5;
}

.pickWrapper-table::-webkit-scrollbar-thumb {
  background-color: #cecece;
}

.pickWrapper-img {
  width: 120px;
  height: 120px;
  margin-left: 10px;
}

.similar-counts {
  font-size: 12px;
}

.not-allowed {
  cursor: not-allowed;
}

:deep(.ant-modal .ant-modal-content) {
  padding: 20px 12px;
}

:deep(.ant-image-preview-operations) {
  background: rgb(0 0 0 / 44%);
}

:deep(.ant-image-preview-root .ant-image-preview-mask) {
  background: rgb(255 255 255);
}

:deep(.pickWrapper-img .ant-image) {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

:deep(.pickWrapper-img .ant-image .ant-image-img) {
  // max-width: 100%;
  width: auto;
  height: auto;
  max-height: 100px;
  max-width: 118px;
}
</style>
