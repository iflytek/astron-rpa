<script setup lang="ts">
import {
  ArrowsAltOutlined,
  CalendarOutlined,
  EllipsisOutlined,
  InfoCircleOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import type { Ref } from 'vue'
import { computed, inject, ref, watch } from 'vue'

import { ATOM_FORM_TYPE } from '@/constants/atom'
import useCursorStore from '@/stores/useCursorStore'
import { ElementPickModal } from '@/views/Arrange/components/pick'
import { ORIGIN_BUTTON } from '@/views/Arrange/config/atom'

import CvPickBtn from '../cvPick/CvPickBtn.vue'

import AtomContractElement from './AtomContractElement.vue'
import AtomGrid from './AtomGrid.vue'
import AtomKeyboard from './AtomKeyboard.vue'
import AtomOptions from './AtomOptions.vue'
import AtomPopover from './AtomPopover.vue'
import AtomRemoteFiles from './AtomRemoteFiles.vue'
import AtomRemoteSelect from './AtomRemoteSelect.vue'
import AtomScriptParams from './AtomScriptParams.vue'
import AtomSlider from './AtomSlider.vue'
import { createDom } from './hooks/useAtomVarPopover'
import { isConditionalKeys } from './hooks/useBaseConfig'
import useRenderFormType, { formBtnHandle, generateInputVal, handleInput, handlePaste, inputListListener, syncCurrentAtomData } from './hooks/useRenderFormType'
import ProcessParam from './ProcessParam.vue'

const { iconStyle, itemData, itemType, varType } = defineProps({
  iconStyle: {
    type: Object,
    default: () => ({}),
  },
  itemType: {
    type: String as () => ATOM_FORM_TYPE,
    default: '',
  },
  itemData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
  varType: {
    type: String,
    default: '',
  },
})

const { handleModalButton, handleTextareaModal, handleHTMLContentPaste } = useRenderFormType()
const isShowFormItem = inject<Ref<boolean>>('showAtomFormItem', ref(true))
const cursorStore = useCursorStore()
const container = ref(generateInputVal(itemData))
const selectValue = ref(generateInputVal(itemData))
const pickLoading = ref(false)
const isEdit = computed(() => !itemData?.noInput) // 是否能编辑 noInput为true时不能编辑

function updateItemToFlowData() {
  syncCurrentAtomData(itemData)
}

watch(
  () => selectValue.value,
  (val) => {
    if (isConditionalKeys(itemData.key))
      isShowFormItem.value = !isShowFormItem.value
    if (itemData?.allowReverse) {
      itemData.allowReverse = false
    }
    itemData.value = val
    updateItemToFlowData()
  },
)

watch(() => itemData.value, () => { // 特殊处理自定义对话框视图多个控件联动更新
  // console.log('itemData.value', itemData.value)
  const { formType: { type }, allowReverse } = itemData
  if (type === ATOM_FORM_TYPE.SELECT && allowReverse) {
    selectValue.value = generateInputVal(itemData)
  }
})

function clickHandle(e?: Event) {
  if (itemType === ATOM_FORM_TYPE.MODALBUTTON) {
    handleModalButton(itemData)
    return
  }
  if (itemType === ATOM_FORM_TYPE.TEXTAREAMODAL) {
    handleTextareaModal(e, itemData)
    return
  }
  if (itemType === ATOM_FORM_TYPE.CONTENTPASTE) {
    handleHTMLContentPaste().then((res) => {
      if (res) {
        handleSetFormDataNF(res)
        createDom({ val: res }, itemData, ORIGIN_BUTTON)
      }
    })
    return
  }

  const extra = [ATOM_FORM_TYPE.PICK, ATOM_FORM_TYPE.MOUSEPOSITION].includes(itemType)
    ? {
        pickLoading,
        elementPickModal: () => NiceModal.show(ElementPickModal),
      }
    : {}
  formBtnHandle(itemData, itemType, extra)
}

// 不会刷新当前配置页
function handleSetFormDataNF(val: any) {
  itemData.value = val
  syncCurrentAtomData(itemData, false)
}

function handleAtomRemoteSelect(val: any) {
  // console.log('val: ', val);
  itemData.value = val.value
  syncCurrentAtomData(itemData, false)
}

inputListListener(itemData, itemType)
</script>

<template>
  <!-- python表达式 -->
  <span
    v-if="itemType === ATOM_FORM_TYPE.PYTHON"
    class="cursor-pointer leading-none"
    @click="clickHandle"
  >
    <rpa-hint-icon :title="itemData.isExpr ? 'python模式' : '普通模式'" :name="itemData.isExpr ? 'create-python-process' : 'change-python-btn'" :style="iconStyle" />
  </span>
  <!-- input框 -->
  <div
    v-if="itemType === ATOM_FORM_TYPE.INPUT"
    :id="`rpa_input_${itemData.key}`"
    class="editor flex-1 min-h-5" :class="{ 'cursor-not-allowed': !isEdit }"
    :contenteditable="isEdit"
    @input="(e) => handleInput(e, itemData)"
    @paste="(e) => handlePaste(e, itemData)"
    @blur="cursorStore.handleBlur"
    v-html="container"
  />
  <!-- CV图片框 -->
  <AtomPopover v-if="itemType === ATOM_FORM_TYPE.CV_IMAGE" :render-type="itemType" :render-data="itemData" tooltip="选择元素">
    <span class="w-5 h-5 flex justify-center items-center relative cursor-pointer">
      <rpa-icon size="16" name="bottom-menu-ele-manage" />
    </span>
  </AtomPopover>
  <!-- 九宫格 -->
  <AtomGrid v-if="itemType === ATOM_FORM_TYPE.GRID" class="cursor-pointer mr-1" :render-data="itemData" @refresh="updateItemToFlowData" />
  <AtomSlider v-if="itemType === ATOM_FORM_TYPE.SLIDER" class="cursor-pointer mr-1" :render-data="itemData" @refresh="updateItemToFlowData" />
  <!-- 文本弹窗 -->
  <ArrowsAltOutlined
    v-if="itemType === ATOM_FORM_TYPE.TEXTAREAMODAL"
    class="cursor-pointer mr-1 opacity-55"
    :style="iconStyle"
    @click="clickHandle"
  />
  <!-- 文件框 -->
  <EllipsisOutlined
    v-if="itemType === ATOM_FORM_TYPE.FILE"
    class="cursor-pointer mr-1"
    :style="iconStyle"
    @click="clickHandle"
  />
  <!-- 变量框 -->
  <AtomPopover
    v-if="itemType === ATOM_FORM_TYPE.VARIABLE"
    :render-type="itemType"
    :render-data="itemData"
    :var-type="varType"
  >
    <rpa-hint-icon name="open-var-btn" title="选择变量" class="cursor-pointer" :style="iconStyle" />
  </AtomPopover>
  <!-- 颜色设置框 -->
  <AtomPopover
    v-if="itemType === ATOM_FORM_TYPE.COLOR"
    :render-type="itemType"
    :render-data="itemData"
  >
    <SettingOutlined class="cursor-pointer mr-1" :style="iconStyle" />
  </AtomPopover>
  <!-- 邮件正文paste -->
  <a-button
    v-if="itemType === ATOM_FORM_TYPE.CONTENTPASTE"
    type="link"
    class="w-[30px] h-[32px] flex items-center justify-center text-inherit"
    @click="clickHandle"
  >
    <template #icon>
      <rpa-hint-icon title="填充内容" size="14" name="bottom-pick-menu-create" />
    </template>
  </a-button>
  <!-- 拾取框 -->
  <AtomPopover v-if="itemType === ATOM_FORM_TYPE.PICK" :render-type="itemType" :render-data="itemData" tooltip="选择元素">
    <a-button type="text" class="flex justify-center items-center">
      <template #icon>
        <rpa-icon size="16" name="bottom-menu-ele-manage" />
      </template>
    </a-button>
  </AtomPopover>
  <!-- CV图片拾取按钮 -->
  <CvPickBtn v-if="itemType === ATOM_FORM_TYPE.CVPICK" type="icon" entry="atomFormBtn" class="h-[32px] w-[32px] justify-center" @click="clickHandle" />
  <!-- 卓越中心共享文件选择 -->
  <AtomRemoteFiles
    v-if="itemType === ATOM_FORM_TYPE.REMOTEFOLDERS"
    :render-data="itemData"
    :render-type="itemType"
    @refresh="handleSetFormDataNF"
  />
  <!-- 单选框 -->
  <a-radio-group
    v-if="itemType === ATOM_FORM_TYPE.RADIO"
    v-model:value="selectValue"
    class="flex"
    :options="itemData.options"
  />
  <!-- 多选框 -->
  <a-checkbox
    v-if="itemType === ATOM_FORM_TYPE.CHECKBOX"
    v-model:checked="selectValue"
  >
    <div class="text-xs inline-flex items-center gap-1">
      {{ itemData.title }}
      <a-tooltip v-if="itemData.tip" :title="itemData.tip">
        <InfoCircleOutlined />
      </a-tooltip>
    </div>
  </a-checkbox>
  <!-- 多选框组 -->
  <a-checkbox-group
    v-if="itemType === ATOM_FORM_TYPE.CHECKBOXGROUP"
    v-model:value="selectValue"
    :options="itemData.options"
  />
  <!-- 开关框 -->
  <a-switch
    v-if="itemType === ATOM_FORM_TYPE.SWITCH"
    v-model:checked="selectValue"
    :checked-value="itemData?.options[0].value"
    :un-checked-value="itemData?.options[1].value"
    :checked-children="itemData?.options[0].label"
    :un-checked-children="itemData?.options[1].label"
  />
  <!-- 下拉框 -->
  <a-select
    v-if="itemType === ATOM_FORM_TYPE.SELECT"
    v-model:value="selectValue"
    :mode="itemData.formType.params?.multiple ? 'multiple' : undefined"
    placeholder="请选择"
    class="bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] rounded-[8px]"
    style="width: 100%;"
  >
    <a-select-option v-for="(op, index) in itemData.options" :key="index" :value="op?.label ? op.value : op.rId">
      <template v-if="op?.label">
        {{ op.label }}
      </template>
      <template v-else>
        <span v-for="(it, idx) in op.value.value" :key="idx">
          <hr v-if="it.type === 'var'" class="dialog-tag-input-hr" :data-name="it.value">
          <span v-else>{{ it.value }}</span>
        </span>
      </template>
    </a-select-option>
  </a-select>
  <AtomRemoteSelect
    v-if="itemType === ATOM_FORM_TYPE.REMOTEPARAMS"
    :render-data="itemData"
    :render-type="itemType"
    @refresh="handleAtomRemoteSelect"
  />
  <!-- 按键框 -->
  <AtomKeyboard
    v-if="itemType === ATOM_FORM_TYPE.KEYBOARD"
    :render-data="itemData"
    :render-type="itemType"
    @refresh="() => syncCurrentAtomData(itemData, false)"
  />
  <!-- 普通字号数字输入框 -->
  <a-input-number
    v-if="itemType === ATOM_FORM_TYPE.FONTSIZENUMBER"
    v-model:value="selectValue"
    :min="itemData.min"
    :max="itemData.max"
    :step="itemData?.step || 1"
    :style="{ width: '100%' }"
  />
  <!-- 弹窗按钮 -->
  <a-button
    v-if="itemType === ATOM_FORM_TYPE.MODALBUTTON"
    type="primary"
    block
    :loading="itemData.formType.params?.loading"
    @click="clickHandle"
  >
    {{ itemData.title }}
  </a-button>

  <!-- 弹窗按钮 -->
  <a-button
    v-if="itemType === ATOM_FORM_TYPE.MOUSEPOSITION"
    type="primary"
    block
    @click="clickHandle"
  >
    获取坐标位置
  </a-button>

  <a-date-picker
    v-if="itemType === ATOM_FORM_TYPE.DATETIME"
    show-time
    value-format="YYYY-MM-DD HH:mm:ss"
    format="YYYY-MM-DD HH:mm:ss"
    :bordered="false"
    :input-read-only="true"
    :style="{ width: '36px', height: '22px' }"
    @ok="(date: string) => { createDom({ val: date }, itemData, ORIGIN_BUTTON); }"
  >
    <template #suffixIcon>
      <CalendarOutlined class="text-primary" />
    </template>
  </a-date-picker>
  <!-- 普通日期选择器 -->
  <a-date-picker
    v-if="itemType === ATOM_FORM_TYPE.DEFAULTDATEPICKER"
    v-model:value="selectValue"
    value-format="YYYY-MM-DD HH:mm:ss"
    :show-time="itemData.formType.params?.format?.split(' ')[1] ? { format: itemData.formType.params?.format?.split(' ')[1] } : false"
    :format="itemData.formType.params?.format || 'YYYY-MM-DD'"
    :style="{ width: '100%' }"
  >
    <template #suffixIcon>
      <CalendarOutlined class="text-primary" />
    </template>
  </a-date-picker>
  <!-- 普通范围日期选择器 -->
  <a-range-picker
    v-if="itemType === ATOM_FORM_TYPE.RANGEDATEPICKER"
    v-model:value="selectValue"
    value-format="YYYY-MM-DD HH:mm:ss"
    :show-time="itemData.formType.params?.format?.split(' ')[1] ? { format: itemData.formType.params?.format?.split(' ')[1] } : false"
    :format="itemData.formType.params?.format || 'YYYY-MM-DD'"
    :style="{ width: '100%' }"
  >
    <template #suffixIcon>
      <CalendarOutlined class="text-primary" />
    </template>
  </a-range-picker>
  <!-- 普通密码输入框 -->
  <a-input-password
    v-if="itemType === ATOM_FORM_TYPE.DEFAULTPASSWORD"
    v-model:value="selectValue"
    :style="{ width: '100%' }"
  />
  <!-- 选项列表options -->
  <AtomOptions
    v-if="itemType === ATOM_FORM_TYPE.OPTIONSLIST"
    :icon-style="iconStyle"
    :render-data="itemData"
    @refresh="handleSetFormDataNF"
  />
  <!-- 子流程配置参数 -->
  <ProcessParam
    v-if="itemType === ATOM_FORM_TYPE.PROCESS_PARAM"
    :render-data="itemData"
    @refresh="handleSetFormDataNF"
  />
  <!-- AI合同要素 -->
  <AtomContractElement
    v-if="itemType === ATOM_FORM_TYPE.FACTORELEMENT"
    :render-data="itemData"
    @refresh="handleSetFormDataNF"
  />
  <!-- JS脚本参数管理 -->
  <AtomScriptParams
    v-if="itemType === ATOM_FORM_TYPE.SCRIPTPARAMS"
    :height="160"
    :params="itemData"
    @refresh="handleSetFormDataNF"
  />
</template>

<style lang="scss" scoped>
.editor {
  width: calc(100% - 42px);
  padding: 0 5px;
  white-space: pre-wrap;
  --custom-cursor-size: 18px;
  margin-right: 3px;
  max-height: 300px;
  overflow: auto;
  &::-webkit-scrollbar {
    width: 4px;
  }

  &:focus {
    outline: none;
  }

  :deep(p) {
    margin: 0;
  }
}

:deep(.ant-radio-wrapper) {
  font-size: 12px;
}

:deep(.ant-select-selector) {
  font-size: 12px;
  background-color: inherit !important;
  color: inherit;
}

:deep(.ant-select-dropdown .ant-select-item) {
  font-size: 12px;
}

.atom-date-time-popover {
  border: none;
  padding: 0;
  border-inline-end-width: 0;
  box-shadow: none;

  :deep(input) {
    font-size: 12px;
    z-index: -1;
    width: 0;
  }
}
</style>
