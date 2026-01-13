import type { Rule } from 'ant-design-vue/es/form'

import type { AnyObj } from '@/types/common'
import type { DialogOption, FormItemConfig } from '@/views/Arrange/components/customDialog/types'

function getPasswordRules(title: string) {
  return [
    {
      validator: (_rule: Rule, value: string) => {
        if (value.length < 4 || value.length > 16) {
          // eslint-disable-next-line prefer-promise-reject-errors
          return Promise.reject(`${title}请输入4-16位字符`)
        }
        return Promise.resolve()
      },
      trigger: 'change',
    },
  ]
}

// 定义自定义对话框数据转换方法
const transformCustom = (data: AnyObj): DialogOption => {
  const { box_title, design_interface, result_button } = data
  const { mode = 'window', buttonType = 'confirm_cancel', formList = [] } = JSON.parse(design_interface || '{}') ?? {}
  const formModel = { result_button } as AnyObj

  const itemList = formList?.map((item) => {
    const { configKeys, dialogFormType } = item
    const res = { dialogFormType } as FormItemConfig
    configKeys.forEach((key) => {
      if (key === 'options') {
        res[key] = item[key].value?.map((op) => ({ label: op.value, value: op.value }))
      }
      else {
        // eslint-disable-next-line no-prototype-builtins
        res[key] = item[key]?.hasOwnProperty('value') ? item[key]?.value : item[key]
      }
    })
    if (configKeys.includes('options') && configKeys.includes('defaultValue')) {
      res.defaultValue = item.options.value.find(op => op.rId === res.defaultValue)?.value || item.defaultValue.defualt
    }
    if (dialogFormType !== 'TEXT_DESC') {
      formModel[res.bind] = res?.defaultValue || res?.defaultPath
    }
    const result = JSON.parse(JSON.stringify(res)) // 过滤掉值为undefined的字段
    if (dialogFormType === 'PASSWORD') { // 密码框统一加上长度校验
      result.rules = getPasswordRules(result.label)
    }
    return result
  })

  return {
    mode,
    title: box_title || '自定义对话框',
    buttonType,
    itemList,
    formModel,
  }
}

// 定义基础对话框数据转换方法
export function transformData(data: AnyObj): DialogOption {
  if (data.key === 'Dialog.custom_box') {
    return transformCustom(data)
  }

  // 获取用户表单选项
  function getUserFormOption(data) {
    let rules = null
    switch (data.key) {
      case 'Dialog.select_box':
        return {
          dialogFormType: data.select_type === 'multi' ? 'MULTI_SELECT' : 'SINGLE_SELECT',
          label: data.options_title,
          options: data?.options?.map((op) => ({ label: op.value, value: op.value })) || [],
          defaultValue: data.select_type === 'multi' ? [] : '',
        }
      case 'Dialog.input_box':
        if (data.input_type !== 'text') {
          rules = getPasswordRules(data.input_title)
        }
        return {
          dialogFormType: data.input_type === 'text' ? 'INPUT' : 'PASSWORD',
          label: data.input_title,
          defaultValue: data.default_input,
          rules,
        }
      case 'Dialog.select_time_box':
        return {
          dialogFormType: data.time_type === 'time' ? 'DATEPICKER' : 'RANGERPICKER',
          label: data.input_title,
          format: data.time_format,
          defaultValue: data.time_type === 'time' ? data.default_time : data.default_time_range,
        }
      case 'Dialog.select_file_box':
        return {
          dialogFormType: 'PATH_INPUT',
          label: data.select_title,
          defaultPath: data.default_path,
          selectType: data.open_type,
          filter: data.file_type,
          isMultiple: data.multiple_choice,
          // defaultValue: data.open_type === 'folder' ? data.default_path : '',
        }
      case 'Dialog.message_box':
        return {
          dialogFormType: 'MESSAGE_CONTENT',
          messageType: data.message_type,
          messageContent: data.message_content,
          defaultValue: data?.default_button || data?.default_button_c || data?.default_button_cn || data?.default_button_y || data?.default_button_yn,
        }
      default:
        break
    }
  }
  const temp = getUserFormOption(data)

  return {
    mode: 'window',
    title: data.box_title || data.box_title_file || data.box_title_folder,
    buttonType: data?.button_type || 'confirm_cancel',
    itemList: [{ bind: data.outputkey, ...temp }],
    formModel: {
      [data.outputkey]: temp?.defaultValue || '',
    },
  }
}
