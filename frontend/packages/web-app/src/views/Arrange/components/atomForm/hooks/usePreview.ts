import { useProcessStore } from '@/stores/useProcessStore'
import { useVariableStore } from '@/stores/useVariableStore'

export function getRealValue(itemValue: any, mark = ''): any {
  if (!Array.isArray(itemValue)) return itemValue

  const processStore = useProcessStore()
  const totalArr = [
    ...useVariableStore().globalVariableList,
    ...(processStore.attributes || [])
  ]
  const variableMap = new Map(totalArr.map((v: any) => [v.varName, v.varValue]))

  return itemValue
    .map((it: any) => (it.type === 'var' ? (variableMap.get(it.value) ?? (mark || it.value)) : it.value))
    .join('')
}

function parseValues(values: Record<string, any>, schema: Record<string, (v: any) => void>) {
  Object.entries(values || {}).forEach(([k, v]) => {
    if (schema[k]) schema[k](v)
  })
}

function getSelectBoxOption(values: Record<string, any>) {
  let title = ''
  let dialogFormType = ''
  let options: any[] = []
  let label = ''

  parseValues(values, {
    box_title: v => (title = getRealValue(v)),
    select_type: v => (dialogFormType = getRealValue(v) === 'multi' ? 'MULTI_SELECT' : 'SINGLE_SELECT'),
    options: v => (options = v),
    options_title: v => (label = getRealValue(v)),
  })

  return { title, itemList: [{ dialogFormType, label, options }] }
}

function getInputBoxOption(values: Record<string, any>) {
  let title = ''
  let dialogFormType = ''
  let label = ''
  let defaultValueTxt: any = ''
  let defaultValuePsd: any = ''

  parseValues(values, {
    box_title: v => (title = getRealValue(v)),
    input_type: v => (dialogFormType = getRealValue(v) === 'text' ? 'INPUT' : 'PASSWORD'),
    input_title: v => (label = getRealValue(v)),
    default_input_text: v => (defaultValueTxt = v),
    default_input_pwd: v => (defaultValuePsd = v),
  })

  return {
    title,
    itemList: [{ dialogFormType, label, defaultValue: dialogFormType === 'INPUT' ? defaultValueTxt : defaultValuePsd }],
  }
}

function getDateBoxOption(values: Record<string, any>) {
  let title = ''
  let dialogFormType = ''
  let label = ''
  let format = ''
  let default_time: any = ''
  let default_time_range: any = ''

  parseValues(values, {
    box_title: v => (title = getRealValue(v)),
    time_type: v => (dialogFormType = getRealValue(v) === 'time' ? 'DATEPICKER' : 'RANGERPICKER'),
    time_format: v => (format = getRealValue(v)),
    default_time: v => (default_time = getRealValue(v)),
    default_time_range: v => (default_time_range = v),
    input_title: v => (label = getRealValue(v)),
  })

  const defaultValue = dialogFormType === 'DATEPICKER' ? default_time : default_time_range
  return { title, itemList: [{ dialogFormType, label, format, defaultValue }] }
}

function getPathBoxOption(values: Record<string, any>) {
  let file_title = ''
  let folder_title = ''
  let label = ''
  let selectType = ''
  let filter = ''
  let isMultiple = true

  parseValues(values, {
    box_title_file: v => (file_title = getRealValue(v)),
    box_title_folder: v => (folder_title = getRealValue(v)),
    open_type: v => (selectType = getRealValue(v)),
    file_type: v => (filter = getRealValue(v)),
    multiple_choice: v => (isMultiple = getRealValue(v)),
    select_title: v => (label = getRealValue(v)),
  })

  const title = selectType === 'file' ? file_title : folder_title
  return { title, itemList: [{ dialogFormType: 'PATH_INPUT', label, selectType, filter, isMultiple }] }
}

function getMessageBoxOption(values: Record<string, any>) {
  let title = ''
  let messageType = ''
  let messageContent: any = ''
  let buttonType = ''

  parseValues(values, {
    box_title: v => (title = getRealValue(v)),
    message_type: v => (messageType = getRealValue(v)),
    message_content: v => (messageContent = v),
    button_type: v => (buttonType = getRealValue(v)),
  })

  return { title, buttonType, itemList: [{ dialogFormType: 'MESSAGE_CONTENT', messageType, messageContent }] }
}

export function getUserFormOption(key: string, values: Record<string, any>) {
  switch (key) {
    case 'Dialog.select_box':
      return getSelectBoxOption(values)
    case 'Dialog.input_box':
      return getInputBoxOption(values)
    case 'Dialog.select_time_box':
      return getDateBoxOption(values)
    case 'Dialog.select_file_box':
      return getPathBoxOption(values)
    case 'Dialog.message_box':
      return getMessageBoxOption(values)
    default:
      return undefined
  }
}
