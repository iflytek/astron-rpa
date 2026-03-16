<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { formItemConfigs } from '@/utils/customComponent'
import { useProcessStore } from '@/stores/useProcessStore'
import AtomOptions from '@/views/Arrange/components/atomForm/AtomOptions.vue'
import { getRealValue } from '@/views/Arrange/components/atomForm/hooks/usePreview'
import { ATOM_FORM_TYPE } from '@/constants/atom'

/**
 * AtomOptions 组件期望的数据格式
 */
type AtomOptionsValue = Array<{
  rId: string
  value: {
    rpa: 'special'
    value: Array<{ type: string; value: any }>
  }
}>

const open = defineModel<boolean>('open', { default: false })

const props = defineProps<{
  formItem?: RPA.AtomDisplayItem
}>()

const processStore = useProcessStore()

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

/**
 * 从 formItemConfigs 自动生成 types 到控件类型的映射关系
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

/**
 * 将 formItem.options 格式转换为 AtomOptions 需要的格式
 */
function convertOptionsToAtomOptionsFormat(options: Array<{ label: string; value: string }> = []) {
  return options.map((opt, index) => ({
    rId: `option_${index}`,
    value: {
      rpa: 'special',
      value: [{ type: 'other', value: opt.label || opt.value }],
    },
  }))
}

/**
 * 将 AtomOptions 返回的格式转换为 formItem.options 格式
 */
function convertAtomOptionsToOptionsFormat(atomOptions: AtomOptionsValue): Array<{ label: string; value: string }> {
  return atomOptions.map((opt) => {
    const realValue = getRealValue(opt.value.value)
    return {
      label: realValue,
      value: realValue,
    }
  })
}

const formItemsMap = new Map(
  formItemConfigs.map(config => {
    const key = generateFormItemKey(config.formType)
    return [key, { ...config, key }]
  })
)
const typesToControlTypesMap = buildTypesToControlTypesMap()
const allControlTypeOptions = Array.from(formItemsMap.values()).map(item => ({
  label: item.title,
  value: item.key,
}))

const selectedControlType = ref<string>('')
const isRequired = ref<boolean>(false)
const optionsData = ref({
  formType: { type: 'INPUT_VARIABLE' },
  key: 'options',
  name: 'options',
  title: '选项',
  value: [] as AtomOptionsValue,
} as unknown as RPA.AtomDisplayItem)

// 根据 types 过滤后的控件类型选项列表
const controlTypeOptions = computed(() => {  
  const targetType = props.formItem?.types || 'Any'
  const allowedTypes = typesToControlTypesMap[targetType]
  
  return allControlTypeOptions.filter(option => {
    const formItem = formItemsMap.get(option.value)
    return allowedTypes.has(formItem?.formType?.type)
  })
})

// 判断当前选择的控件类型是否需要选项
const needsOptions = computed(() => {
  if (!selectedControlType.value) return false
  const baseFormItem = formItemsMap.get(selectedControlType.value)
  if (!baseFormItem) return false
  const formType = baseFormItem.formType?.type
  return formType === ATOM_FORM_TYPE.SELECT || formType === ATOM_FORM_TYPE.CHECKBOXGROUP
})

function handleOptionsRefresh(optionResArr: AtomOptionsValue) {
  optionsData.value.value = optionResArr as any
}

async function handleOk() {
  if (!props.formItem) return
  
  const baseFormItem = formItemsMap.get(selectedControlType.value)
  if (!baseFormItem) return
  
  const varName = props.formItem.key
  const parameter = processStore.parameters.find(p => p.varName === varName)
  
  if (!parameter) return
  
  const optionsValue = optionsData.value.value as AtomOptionsValue
  const options = needsOptions.value && optionsValue.length > 0
    ? convertAtomOptionsToOptionsFormat(optionsValue)
    : baseFormItem.options
  
  const updatedFormItem = {
    ...props.formItem,
    formType: baseFormItem.formType,
    options,
    required: isRequired.value,
  }
  
  await processStore.updateParameter({
    ...parameter,
    formItem: JSON.stringify(updatedFormItem),
  })
  
  open.value = false
}

// 当打开弹窗时，初始化数据
watch(() => open.value, (isOpen) => {
  if (isOpen && props.formItem) {
    selectedControlType.value = generateFormItemKey(props.formItem.formType)
    isRequired.value = props.formItem.required || false
    
    // 判断是否需要选项
    const formType = props.formItem.formType?.type
    const needsOpts = formType === ATOM_FORM_TYPE.SELECT || formType === ATOM_FORM_TYPE.CHECKBOXGROUP
    
    optionsData.value.value = (needsOpts && props.formItem.options
      ? convertOptionsToAtomOptionsFormat(props.formItem.options)
      : []) as any
  }
})
</script>

<template>
  <a-modal
    v-model:open="open"
    title="编辑控件"
    :width="400"
    @ok="handleOk"
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
      <div v-if="needsOptions" class="flex flex-col gap-2">
        <label class="text-xs leading-[22px] text-text-tertiary font-medium">选项列表</label>
        <AtomOptions
          :render-data="optionsData"
          @refresh="handleOptionsRefresh"
        />
      </div>
      <div class="flex items-center gap-2">
        <a-checkbox v-model:checked="isRequired" />
        <span class="text-xs">设置为必填项</span>
      </div>
    </div>
  </a-modal>
</template>
