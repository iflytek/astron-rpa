<!-- @format -->

<script lang="ts" setup>
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { message, RangePicker } from 'ant-design-vue'
import dayjs from 'dayjs'
import { useTranslation } from 'i18next-vue'
import { defineEmits, h, reactive, ref, toRaw, watch } from 'vue'

import { usePickStore } from '@/stores/usePickStore'
import CustomTable from '@/views/Arrange/components/pick/CustomTable.vue'
import DirectoryTable from '@/views/Arrange/components/pick/DirectoryTable.vue'
import { CUSTOMIZATION, VISUALIZATION } from '@/views/Arrange/config/pick'
import { elementCustomFormat, elementCustomFormatRecover, elementDirectoryFormat, elementDirectoryFormatRecover } from '@/views/Arrange/utils/elementsUtils'

import { dateSelectList, expSelectList } from './config'
import 'dayjs/locale/zh-cn'

const props = defineProps({
  config: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['afterClose', 'ok'])

// 设置本地化
dayjs.locale('zh-cn')
const { t } = useTranslation()
const expSelectListData = expSelectList.map((item) => {
  return {
    label: t(`dataBatchExpSelectList.${item.key}`),
    options: item.options.map(option => ({
      ...option,
      label: t(`dataBatchExpSelectList.${option.key}`),
    })),
  }
})

const dateSelectListData = dateSelectList.map((item) => {
  return {
    label: t(`dataBacthDateSelectList.${item.key}`),
    value: item.value,
    key: item.key,
  }
})

const usePick = usePickStore()
const modalConfig = reactive({
  open: false,
  title: '',
  width: '400px',
  warpClassName: '',
  type: '',
  column: null,
})

const activeKey = ref(VISUALIZATION)
const customData = ref<any>([])
const directoryData = ref<any>([])
const isShadow = ref(false)

const replaceConfig = reactive({
  processType: 'Replace',
  isEnable: 1,
  parameters: [],
})
const suffixConfig = reactive({
  processType: 'Suffix',
  isEnable: 1,
  parameters: [{
    val: '',
  }],
})
const prefixConfig = reactive({
  processType: 'Prefix',
  isEnable: 1,
  parameters: [{
    val: '',
  }],
})
const formatTimeConfig = reactive({
  processType: 'FormatTime',
  isEnable: 1,
  parameters: [{
    val: '',
  }],
})
const regularConfig = reactive({
  processType: 'Regular',
  isEnable: 1,
  parameters: [{
    val: '',
  }],
})

const filterAssociation = ref('and')
function okFn() {
  if (usePick.isChecking)
    return
  const res = handleOk()
  if (res) {
    modalConfig.open = false
    emit('ok', modalConfig)
  }
}

function handleOk() {
  const config = {
    Replace: replaceHandle,
    Suffix: suffixHandle,
    Prefix: prefixHandle,
    FormatTime: formatTimeHandle,
    Regular: regularHandle,
    editColumnElement: editColumnElementHandle,
    // colFilterConfig: colFilterConfigHandle,
    // filterConfig: filterConfigHandle,
  }
  return config[modalConfig.type] ? config[modalConfig.type]() : true
}

function replaceHandle() {
  if (replaceConfig.parameters.length === 0) {
    message.warn(t('dataBatch.addReplace'))
    return false
  }
  const replaceItem = modalConfig.column.colDataProcessConfig.find((item: any) => item.processType === 'Replace')
  if (replaceItem) {
    replaceItem.isEnable = 1
    replaceItem.parameters = replaceConfig.parameters
  }
  else {
    modalConfig.column.colDataProcessConfig.push(replaceConfig)
  }
  return true
}

function suffixHandle() {
  if (suffixConfig.parameters[0].val === '') {
    message.warn(t('dataBatch.addSuffix'))
    return false
  }
  const suffixItem = modalConfig.column.colDataProcessConfig.find((item: any) => item.processType === 'Suffix')
  if (suffixItem) {
    suffixItem.isEnable = 1
    suffixItem.parameters = suffixConfig.parameters
  }
  else {
    modalConfig.column.colDataProcessConfig.push(suffixConfig)
  }
  return true
}

function prefixHandle() {
  if (prefixConfig.parameters[0].val === '') {
    message.warn(t('dataBatch.addPrefix'))
    return false
  }
  const prefixItem = modalConfig.column.colDataProcessConfig.find((item: any) => item.processType === 'Prefix')
  if (prefixItem) {
    prefixItem.isEnable = 1
    prefixItem.parameters = prefixConfig.parameters
  }
  else {
    modalConfig.column.colDataProcessConfig.push(prefixConfig)
  }
  return true
}

function formatTimeHandle() {
  if (formatTimeConfig.parameters[0].val === '') {
    message.warn(t('dataBatch.addFormatTime'))
    return false
  }
  const formatTimeItem = modalConfig.column.colDataProcessConfig.find((item: any) => item.processType === 'FormatTime')
  if (formatTimeItem) {
    formatTimeItem.isEnable = 1
    formatTimeItem.parameters = formatTimeConfig.parameters
  }
  else {
    modalConfig.column.colDataProcessConfig.push(formatTimeConfig)
  }
  return true
}

function regularHandle() {
  if (regularConfig.parameters[0].val === '') {
    message.warn(t('dataBatch.addRegular'))
    return false
  }
  const regularItem = modalConfig.column.colDataProcessConfig.find((item: any) => item.processType === 'Regular')
  if (regularItem) {
    regularItem.isEnable = 1
    regularItem.parameters = regularConfig.parameters
  }
  else {
    modalConfig.column.colDataProcessConfig.push(regularConfig)
  }
  return true
}

function modalType(args: any) {
  const { version, type } = modalConfig.column
  if (args.type === 'editColumnElement') {
    if (modalConfig.column?.shadowRoot) {
      isShadow.value = true
      activeKey.value = CUSTOMIZATION
    }
    customData.value = elementCustomFormat(version, type, modalConfig.column)
    directoryData.value = elementDirectoryFormat(version, type, modalConfig.column)
  }
}

function editColumnElementHandle() {
  const { version, type } = modalConfig.column
  const customDataMap = toRaw(elementCustomFormatRecover(version, type, customData.value)) // url, xpath, cssSelector
  const pathDirs = toRaw(elementDirectoryFormatRecover(version, type, directoryData.value)) // pathDirs
  modalConfig.column = {
    ...modalConfig.column,
    ...customDataMap,
    pathDirs,
    checkType: activeKey.value,
    matchTypes: [], // 默认空数组
  }
  return true
}

function openModal(args: any) {
  console.log('openModal: ', args)
  Object.assign(modalConfig, args)
  modalConfig.open = true
  modalType(args)
  initModalData()
}
function afterCloseFn() {
  reset()
}

function reset() {
  modalConfig.open = false
  modalConfig.title = ''
  modalConfig.width = '400px'
  modalConfig.warpClassName = ''
  modalConfig.type = ''
  activeKey.value = VISUALIZATION
  customData.value = []
  directoryData.value = []
  modalConfig.column = null
}

function checkElements() {
  const { version, type } = modalConfig.column
  const customDataMap = toRaw(elementCustomFormatRecover(version, type, customData.value)) // url, xpath, cssSelector
  const pathDirs = toRaw(elementDirectoryFormatRecover(version, type, directoryData.value)) // pathDirs
  modalConfig.column = {
    ...modalConfig.column,
    ...customDataMap,
    pathDirs,
    checkType: activeKey.value,
    matchTypes: [], // 默认空数组
  }
  const checkParam = {
    app: modalConfig.column.app,
    type: modalConfig.column.type,
    version: modalConfig.column.version,
    path: modalConfig.column,
  }
  const elements = JSON.stringify(checkParam)
  usePick.startCheck('', elements, (res) => {
    if (res.success) {
      message.success('校验成功')
    }
  }, 'restore')
}

function deleteFilter(index: number, arr: any[]) {
  arr.splice(index, 1)
}

function addFilter(arr: any[]) {
  const exp = {
    logical: '==',
    parameter: '',
  }
  arr.push(exp)
}

function deleteReplace(index: number) {
  replaceConfig.parameters.splice(index, 1)
}

function addReplace() {
  const exp = {
    text: '',
    replaceText: '',
  }
  replaceConfig.parameters.push(exp)
}

function prefixSuffixText(type: string) {
  return {
    Prefix: t('dataBatch.prefix'),
    Suffix: t('dataBatch.suffix'),
  }[type]
}
// 过滤条件的value input 显示
function showfilterValueInput(type: string) {
  const showMap = {
    isnull: 'empty',
    notnull: 'empty',
    time_befor: 'time',
    time_after: 'time',
    time_between: 'time_between',
  }
  return showMap[type] || 'input'
}

function inputPlaceholder(type: string) {
  if (type === 'enumerate') {
    return t('dataBatch.enumPlaceholder')
  }
  else {
    return t('dataBatch.conditionPlaceholder')
  }
}
function filterSelectChange(item) {
  console.log('item: ', item)
  if (item.logical === 'time_between') {
    item.parameter = ['', '']
  }
  else if (item.logical === 'enumerate') {
    item.parameter = ''
  }
  else {
    item.parameter = ''
  }
}

function initModalData() {
  if (modalConfig.type === 'filterConfig') {
    filterAssociation.value = modalConfig.column?.filterConfig[0]?.filterAssociation || 'and'
  }
  if (modalConfig.type === 'colFilterConfig') {
    filterAssociation.value = modalConfig.column?.colFilterConfig[0]?.filterAssociation || 'and'
  }
  const processTypes = ['Replace', 'Suffix', 'Prefix', 'FormatTime', 'Regular']
  if (processTypes.includes(modalConfig.type)) {
    const configMap = {
      Replace: replaceConfig,
      Suffix: suffixConfig,
      Prefix: prefixConfig,
      FormatTime: formatTimeConfig,
      Regular: regularConfig,
    }
    processTypes.forEach((type) => {
      const item = modalConfig.column?.colDataProcessConfig.find(item => item.processType === type)
      if (item) {
        configMap[type].isEnable = item.isEnable
        configMap[type].parameters = item.parameters
      }
    })
  }
}
const getContainer = () => document.querySelector('#dataBatch') as HTMLElement

defineExpose({
  openModal,
})

watch(() => props.config, (newVal) => {
  if (newVal.open) {
    openModal(newVal)
  }
}, {
  immediate: true,
})
</script>

<template>
  <a-modal
    v-model:open="modalConfig.open"
    :destroy-on-close="true"
    :wrap-class-name="modalConfig.warpClassName"
    :width="modalConfig.width"
    :after-close="afterCloseFn"
    :get-container="getContainer"
    :title="modalConfig.title"
    class="batch-modal-root"
    @ok="okFn"
    @cancel="modalConfig.open = false"
  >
    <div class="batch-modal">
      <!-- 编辑元素 -->
      <div v-if="modalConfig.type === 'editColumnElement'" class="batch-modal-content">
        <div class="absolute check-button">
          <a-button type="primary" class="text-[12px]" @click="checkElements">
            {{ t('validateElement') }}
          </a-button>
        </div>
        <a-tabs v-model:active-key="activeKey">
          <a-tab-pane v-if="!isShadow" :key="VISUALIZATION" :tab="t('visualEditing')" class="text-[12px]">
            <DirectoryTable id="visualization" :node-source="directoryData" />
          </a-tab-pane>
          <a-tab-pane :key="CUSTOMIZATION" :tab="t('customEditing')" class="text-[12px]">
            <CustomTable id="customization" :custom-data="customData" />
          </a-tab-pane>
        </a-tabs>
      </div>
      <!-- 编辑列名 -->
      <div v-if="modalConfig.type === 'editColumnName'" class="batch-modal-content flex items-center">
        <span class="mr-2">{{ t('dataBatch.columnName') }}:</span> <a-input v-model:value="modalConfig.column.title" class="flex-1" />
      </div>
      <!-- 列筛选 type colFilterConfig, 包含一个AND /OR 的radio, 和多个条件1，2，3 每个条件有等于等操作符号 -->
      <div v-if="'colFilterConfig' === modalConfig.type" class="batch-modal-content text-[12px]">
        <a-radio-group v-model:value="filterAssociation">
          <a-radio value="and" class="text-[12px]">
            {{ t('dataBatch.allCondition') }}
          </a-radio>
          <a-radio value="or" class="text-[12px]">
            {{ t('dataBatch.anyCondition') }}
          </a-radio>
        </a-radio-group>
        <div class="filter-box mt-2 text-[12px]">
          <div v-for="(item, index) in modalConfig.column.colFilterConfig" :key="index" class="flex justify-between items-center mb-2">
            <span>{{ t('dataBatch.condition') }}{{ index + 1 }}</span>
            <a-select v-model:value="item.logical" class="filter-select ml-2 text-[12px]" :options="expSelectListData" @change="filterSelectChange(item)" />
            <a-input v-if="showfilterValueInput(item.logical) === 'input'" v-model:value="item.parameter" class="filter-input ml-2 text-[12px]" :placeholder="inputPlaceholder(item.logical)" />
            <div v-if="showfilterValueInput(item.logical) === 'empty'" class="empty-value filter-input text-[12px]" />
            <a-date-picker
              v-if="showfilterValueInput(item.logical) === 'time'"
              v-model:value="item.parameter"
              class="ml-2 filter-input text-[12px]"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY/MM/DD HH:mm:ss"
            />
            <RangePicker
              v-if="showfilterValueInput(item.logical) === 'time_between'"
              v-model:value="item.parameter"
              class="ml-2 filter-input text-[12px]"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY/MM/DD HH:mm:ss"
            />
            <DeleteOutlined class="filter-del mr-2" @click="deleteFilter(index, modalConfig.column.colFilterConfig)" />
          </div>
          <a-button class="add-btn text-small" size="small" :icon="h(PlusOutlined)" @click="addFilter(modalConfig.column.colFilterConfig)">
            {{ t('dataBatch.addCondition') }}
          </a-button>
        </div>
      </div>
      <!-- 表格筛选 type filterConfig, 包含一个AND /OR 的radio, 和多个条件1，2，3 每个条件有等于等操作符号 -->
      <div v-if="'filterConfig' === modalConfig.type" class="batch-modal-content text-[12px]">
        <a-radio-group v-model:value="filterAssociation">
          <a-radio value="and" size="small" class="text-[12px]">
            {{ t('dataBatch.allCondition') }}
          </a-radio>
          <a-radio value="or" size="small" class="text-[12px]">
            {{ t('dataBatch.anyCondition') }}
          </a-radio>
        </a-radio-group>
        <div class="filter-box mt-2 text-[12px]">
          <div v-for="(item, index) in modalConfig.column.filterConfig" :key="index" class="flex items-center mb-2 relative">
            <span>{{ t('dataBatch.condition') }}{{ index + 1 }}</span>
            <a-select v-model:value="item.logical" class="filter-select ml-2 text-[12px]" :options="expSelectListData" @change="filterSelectChange(item)" />
            <a-input v-show="showfilterValueInput(item.logical) === 'input'" v-model:value="item.parameter" class="filter-input ml-2 text-[12px]" :placeholder="inputPlaceholder(item.logical)" />
            <div v-show="showfilterValueInput(item.logical) === 'empty'" class="empty-value filter-input text-[12px]" />
            <a-date-picker
              v-show="showfilterValueInput(item.logical) === 'time'"
              v-model:value="item.parameter"
              class="ml-2 filter-input text-[12px]"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY/MM/DD HH:mm:ss"
            />
            <RangePicker
              v-show="showfilterValueInput(item.logical) === 'time_between'"
              v-model:value="item.parameter"
              class="ml-2 filter-input text-[12px]"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY/MM/DD HH:mm:ss"
            />
            <DeleteOutlined class="filter-del mr-2 absolute right-5" @click="deleteFilter(index, modalConfig.column.filterConfig)" />
          </div>
          <a-button class="add-btn text-[12px]" size="small" :icon="h(PlusOutlined)" @click="addFilter(modalConfig.column.filterConfig)">
            {{ t('dataBatch.addCondition') }}
          </a-button>
        </div>
      </div>
      <!-- 字符串替换 -->
      <div v-if="modalConfig.type === 'Replace'" class="batch-modal-content">
        <div class="flex justify-between items-center mb-2 text-[12px]">
          <div class="text-left w-1/2">
            {{ t('dataBatch.beforeReplace') }}:
          </div>
          <div class="text-left w-1/2">
            {{ t('dataBatch.afterReplace') }}:
          </div>
          <div style="width: 22px;" />
        </div>
        <div class="filter-box">
          <div v-for="(item, index) in replaceConfig.parameters" :key="index" class="flex justify-between items-center mb-2">
            <div class="text-left w-1/2">
              <a-input v-model:value="item.text" class="replace-input text-[12px]" />
            </div>
            <div class="text-left w-1/2">
              <a-input v-model:value="item.replaceText" class="replace-input text-[12px]" />
            </div>
            <div> <DeleteOutlined class="filter-del mr-2" @click="deleteReplace(index)" /></div>
          </div>
          <a-button class="add-btn text-small text-[12px]" size="small" :icon="h(PlusOutlined)" @click="addReplace()">
            {{ t('dataBatch.addReplace') }}
          </a-button>
        </div>
      </div>
      <!-- 前缀后缀 -->
      <div v-if="['Prefix', 'Suffix'].includes(modalConfig.type)" class="batch-modal-content">
        <div class="flex justify-between items-center mb-2 prefix-box">
          <div class="text-left text-[12px]">
            {{ prefixSuffixText(modalConfig.type) }}：
          </div>
          <a-input v-if="modalConfig.type === 'Prefix'" v-model:value="prefixConfig.parameters[0].val" class="prefix-input text-[12px]" />
          <a-input v-if="modalConfig.type === 'Suffix'" v-model:value="suffixConfig.parameters[0].val" class="prefix-input text-[12px]" />
        </div>
      </div>

      <!-- 日期时间格式化 -->
      <div v-if="modalConfig.type === 'FormatTime'" class="batch-modal-content">
        <div class="flex items-center mb-2 formattime-box">
          <div class="text-left text-[12px]">
            {{ t('dataBatch.chooseFormat') }}：
          </div>
          <a-select v-model:value="formatTimeConfig.parameters[0].val" class="formattime-select text-[12px]" :options="dateSelectListData" />
        </div>
      </div>

      <!-- 正则表达式 -->
      <div v-if="modalConfig.type === 'Regular'" class="batch-modal-content">
        <div class="flex justify-between items-center mb-2">
          <a-textarea v-model:value="regularConfig.parameters[0].val" :rows="4" class="filter-input text-[12px]" style="resize: none;" :placeholder="t('dataBatch.addRegular')" />
        </div>
      </div>
    </div>
  </a-modal>
</template>

<style lang="scss">
.ant-modal-root .full-modal {
  overflow: hidden;
}
.full-modal {
  display: flex;
  align-items: center;
  justify-content: center;
  .ant-modal {
    top: 16px;
    box-sizing: border-box;
  }

  #customization {
    height: 228px;
    overflow-y: auto;
  }

  .check-button {
    right: 24px;
    top: 60px;
    z-index: 10;
  }
}

.text-small {
  font-size: 12px;
}

.batch-modal-content {
  .filter-box {
    height: 120px;
    overflow-y: auto;
    color: rgb(74, 74, 74);

    .filter-select {
      width: 130px;
    }

    .filter-input {
      width: 180px;
      // max-width: 200px;
    }

    .filter-del {
      color: rgb(105, 105, 105);
    }

    .filter-del:hover {
      color: #ff4d4f;
    }

    .replace-input {
      width: 140px;
    }

    .add-btn {
      .anticon {
        vertical-align: 0.08rem;
      }
    }
  }

  .formattime-box {
    height: 80px;

    .formattime-select {
      flex: 1;
    }
  }

  .prefix-box {
    height: 80px;

    .prefix-input {
      flex: 1;
    }
  }
}

.dark .batch-modal-root .title {
  color: #fafafa;
}
.batch-modal-root .ant-select-selection-item {
  font-size: 12px;
}
.batch-modal-root .ant-select-selector {
  height: 28px;
}
.batch-modal-root .ant-btn.ant-btn-sm {
  font-size: 12px;
}
.batch-modal-root .ant-picker .ant-picker-input > input {
  font-size: 12px;
}

.batch-modal-root .ant-tabs .ant-tabs-tab {
  font-size: 12px;
}
</style>
