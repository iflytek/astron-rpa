<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import type { Ref } from 'vue'
import { computed, inject, ref, watch } from 'vue'

import BUS from '@/utils/eventBus'
import { ATOM_FORM_TYPE } from '@/constants/atom'

import AtomFormItem from '@/views/Arrange/components/atomForm/AtomFormItem.vue'
import { renderBaseConfig, useBaseConfig } from '@/views/Arrange/components/atomForm/hooks/useBaseConfig'
import type { AtomTabs } from '@/views/Arrange/types/atomForm'
import { useToggle } from '@vueuse/core'

const props = defineProps<{
  atom: RPA.Atom
  showCollapse?: boolean
}>()

const emit = defineEmits<{
  (e: 'collapse', v: boolean)
}>()

const { i18next, t } = useTranslation()
const isShowFormItem = inject<Ref<boolean>>('showAtomFormItem', ref(true))

const activeKey = ref<number>(0)
const atomTab = ref<AtomTabs[]>([])
const formattedTabs = computed(() => atomTab.value.map((item, index) => ({
  title: item.name,
  value: index,
})))

const editControlForm = ref<RPA.AtomDisplayItem>() // 编辑控件表单
const [visible, toggleVisible] = useToggle() // 编辑控件弹窗

/**
 * 生成表单配置的唯一key
 */
function generateFormItemKey(formType: RPA.AtomDisplayItem['formType']): string {
  if (!formType) return ''
  const { type, params } = formType
  if (!params || Object.keys(params).length === 0) {
    return type
  }
  const paramsStr = JSON.stringify(params, Object.keys(params).sort())
  return `${type}__${paramsStr}`
}

const formItemConfigs = [
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.PYTHON}_${ATOM_FORM_TYPE.VARIABLE}` },
    title: '标准输入框',
    types: ['Any', 'Float', 'Int', 'Str', 'List', 'Dict', 'PATH', 'DIRPATH', 'Date', 'URL', 'Password', 'Browser', 'DocumentObject', 'ExcelObj'],
    value: '',
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.PYTHON}_${ATOM_FORM_TYPE.VARIABLE}_${ATOM_FORM_TYPE.TEXTAREAMODAL}` },
    title: '多行输入框',
    types: ['Any', 'Str', 'List', 'Dict'],
    value: '',
  },
  {
    formType: { type: ATOM_FORM_TYPE.FONTSIZENUMBER },
    title: '数字输入框',
    types: ['Any', 'Float', 'Int'],
    value: 0,
  },
  {
    formType: { type: ATOM_FORM_TYPE.CHECKBOX },
    title: '复选框',
    types: ['Any', 'Bool'],
    value: false,
  },
  {
    formType: { type: ATOM_FORM_TYPE.SWITCH },
    title: '开关框',
    types: ['Any', 'Bool'],
    value: false,
  },
  {
    formType: { type: ATOM_FORM_TYPE.SELECT, params: { multiple: false } },
    title: '单选下拉框',
    types: ['Any', 'Str', 'List'],
    value: [],
    options: [
      { label: '选项1', value: 'option1' },
      { label: '选项2', value: 'option2' },
      { label: '选项3', value: 'option3' },
    ],
  },
  {
    formType: { type: ATOM_FORM_TYPE.SELECT, params: { multiple: true } },
    title: '多选下拉框',
    types: ['Any', 'Str', 'List'],
    value: [],
    options: [
      { label: '选项1', value: 'option1' },
      { label: '选项2', value: 'option2' },
      { label: '选项3', value: 'option3' },
    ],
  },
  {
    formType: { type: ATOM_FORM_TYPE.CHECKBOXGROUP },
    title: '复选框组',
    types: ['Any', 'Str', 'List'],
    value: [],
    options: [
      { label: '选项1', value: 'option1' },
      { label: '选项2', value: 'option2' },
      { label: '选项3', value: 'option3' },
    ],
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.FILE}` },
    title: '文件选择框',
    types: ['Any', 'PATH', 'DIRPATH'],
    value: '',
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.DATETIME}` },
    title: '日期时间选择器',
    types: ['Any', 'Date'],
    value: '',
  },
  {
    formType: { type: ATOM_FORM_TYPE.DEFAULTDATEPICKER },
    title: '普通日期选择器',
    types: ['Any', 'Date'],
    value: '',
  },
  {
    formType: { type: ATOM_FORM_TYPE.RANGEDATEPICKER },
    title: '范围日期选择器',
    types: ['Any', 'List'],
    value: [],
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.VARIABLE}_${ATOM_FORM_TYPE.PICK}` },
    title: '元素拾取框',
    types: ['Any', 'WebPick', 'WinPick'],
    value: '',
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.VARIABLE}` },
    title: '变量选择框',
    types: ['Any', 'WebPick', 'WinPick'],
    value: '',
  },
  {
    formType: { type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.CV_IMAGE}_${ATOM_FORM_TYPE.CVPICK}` },
    title: '图像拾取框',
    types: ['Any', 'IMGPick'],
    value: '',
  },
  {
    formType: { type: ATOM_FORM_TYPE.DEFAULTPASSWORD },
    title: '密码输入框',
    types: ['Any', 'Password'],
    value: '',
  },
]

const formItemsMap = new Map(
  formItemConfigs.map(config => {
    const key = generateFormItemKey(config.formType)
    return [key, { ...config, key }]
  })
)

/**
 * 从 formItemConfigs 自动生成 types 到控件类型的映射关系
 * 每个配置项的 types 字段为数组，支持一个控件对应多个类型
 */
function buildTypesToControlTypesMap(): Record<string, Set<string>> {
  const map: Record<string, Set<string>> = {}
  
  formItemConfigs.forEach(config => {
    const formType = config.formType?.type
    if (!formType) return
    
    config.types.forEach(type => {
      if (!type) return
      if (!map[type]) {
        map[type] = new Set()
      }
      map[type].add(formType)
    })
  })
  
  return map
}

// types 到控件类型的映射关系
const typesToControlTypesMap = buildTypesToControlTypesMap()

// 所有控件类型选项
const allControlTypeOptions = Array.from(formItemsMap.values()).map(item => ({
  label: item.title,
  value: item.key,
}))

// 根据 types 过滤后的控件类型选项列表
const controlTypeOptions = computed(() => {  
  const targetType = editControlForm.value?.types || 'Any'
  const allowedTypes = typesToControlTypesMap[targetType]
  
  return allControlTypeOptions.filter(option => {
    const formItem = formItemsMap.get(option.value)
    return allowedTypes.has(formItem?.formType?.type)
  })
})

// 当前选择的控件类型
const selectedControlType = ref<string>('')
// 是否必填
const isRequired = ref<boolean>(false)

function handleOk() {
  if (editControlForm.value) {
    const baseFormItem = formItemsMap.get(selectedControlType.value)
    if (baseFormItem) {
      Object.assign(editControlForm.value, {
        formType: baseFormItem.formType,
        options: baseFormItem.options,
        value: baseFormItem.value,
        required: isRequired.value,
      })
    }
  }
  
  editControlForm.value = undefined
  toggleVisible(false)
}

function handleCancel() {
  editControlForm.value = undefined
  toggleVisible(false)
}

function handleEdit(form: RPA.AtomDisplayItem) {
  editControlForm.value = form
  selectedControlType.value = generateFormItemKey(form.formType)
  isRequired.value = form.required || false
  toggleVisible(true)
}

function renderForm(atom: RPA.Atom) {
  atomTab.value = atom ? useBaseConfig(atom, t) : []
}

watch(() => isShowFormItem.value, () => {
  atomTab.value = renderBaseConfig(atomTab.value)
})

watch(() => props.atom, (newVal, oldVal) => {
  if (!newVal?.key) {
    BUS.$emit('toggleAtomForm', false)
  }
  if (newVal?.key !== oldVal?.key) {
    activeKey.value = 0
  }
  renderForm(newVal)
  console.log('atomForm', atomTab.value)
}, { immediate: true })

const alias = computed(() => atomTab.value
  .find(item => item.key === 'baseParam')
  .params[0]
  .formItems
  .find(item => item.key === 'anotherName')
  .value[0]
  .value,
)

watch(() => alias.value, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    props.atom.alias = newVal
  }
}, { deep: true })
</script>

<template>
  <div v-if="atomTab.length > 0" class="h-full flex flex-col gap-4 bg-bg-elevated">
    <div class="flex items-center gap-2">
      <a-segmented v-model:value="activeKey" block :options="formattedTabs" class="flex-1">
        <template #label="{ title }">
          <span class="text-[12px]">{{ $t(title) }}</span>
        </template>
      </a-segmented>
      <rpa-hint-icon
        v-if="showCollapse"
        :title="$t('common.collapse')"
        name="navigate-expand"
        enable-hover-bg
        class="p-1.5"
        @click="emit('collapse', true)" />
    </div>

    <div class="form-container flex-1 flex flex-col gap-6 overflow-y-auto">
      <section
        v-for="item in atomTab[activeKey]?.params"
        :key="item.key"
        class="text-[12px]"
      >
        <label v-if="item.name" class="text-[14px] font-bold mb-3 inline-block">
          {{ item.name[i18next.language] }}
        </label>
        <template
          v-for="form in item.formItems?.filter(item => !item.dynamics || [undefined, true].includes(item.show))"
          :key="form.key"
        >
          <template v-if="item.key.startsWith('input')">
            <div class="group relative p-1.5" @click="handleEdit(form)">
              <AtomFormItem :atom-form-item="form" />
              <!-- <div class="mt-2 pt-2 border-t border-[#000000]/[.08] dark:border-[#FFFFFF]/[.08]">
                <div class="text-[10px] text-[#000000]/[.45] dark:text-[#FFFFFF]/[.45] mb-1">
                  Value (实时):
                </div>
                <pre class="text-[10px] text-[#000000]/[.85] dark:text-[#FFFFFF]/[.85] bg-[#ffffff] dark:bg-[#2a2a2a] p-2 rounded overflow-x-auto max-h-[120px] overflow-y-auto font-mono whitespace-pre-wrap break-words">{{ form.value }}</pre>
                <div class="text-[9px] text-[#000000]/[.35] dark:text-[#FFFFFF]/[.35] mt-1">
                  类型: {{ Array.isArray(form.value) ? 'Array' : typeof form.value }}
                </div>
              </div> -->
              <div class="absolute inset-0 rounded-lg hover:bg-[#5D59FF]/[.35] cursor-pointer"></div>
              <rpa-icon
                name="edit-outline"
                size="20"
                class="invisible group-hover:visible absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none"
              />
            </div>
          </template>
          <template v-else>
            <AtomFormItem :atom-form-item="form" disabled />
          </template>
        </template>
      </section>
    </div>

    <a-modal
      v-model:open="visible"
      title="编辑控件"
      :width="400"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label class="text-xs leading-[22px] text-text-tertiary font-medium">输入控件类型</label>
          <a-select
            v-model:value="selectedControlType"
            :options="controlTypeOptions as any"
            placeholder="请选择控件类型"
            class="w-full"
          />
        </div>
        <div class="flex items-center gap-2">
          <a-checkbox v-model:checked="isRequired" />
          <span class="text-xs">设置为必填项</span>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<style lang="scss" scoped>
.form-container {
  padding-right: 2px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  :deep(.form-container-label-name) {
    color: var(--text-text-tertiary);
  }
}
</style>
  