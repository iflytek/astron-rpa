import { CloseCircleOutlined, ExclamationCircleOutlined, InfoCircleOutlined, QuestionCircleOutlined, UploadOutlined } from '@ant-design/icons-vue'
import { Checkbox, DatePicker, Input, Radio, RangePicker, Select, Tag } from 'ant-design-vue'
import { nanoid } from 'nanoid'
import { omit } from 'lodash-es'

import { utilsManager } from '@/platform'

import TagInputUser from '../components/tagInputUser.vue'
import { fontFamilyMap, fontStyleMap } from '../config'

/**
 * 生成输入框
 */
function renderInput(item, modelObj = {}) {
  const nodeProps = omit(item, ['dialogFormType', 'bind', 'label', 'required'])
  
  if (Array.isArray(item?.defaultValue)) { // 处理变量预览的情况
    return <TagInputUser itemData={item} />
  }
  return (
    <Input
      v-model:value={modelObj[item.bind]}
      allowClear
      autocomplete="off"
      {...nodeProps}
    />
  )
}

/**
 * 生成密码框
 */
function renderPassword(item, modelObj = {}) {
  const nodeProps = omit(item, ['dialogFormType', 'bind', 'label', 'required'])
  return (
    <Input.Password
      v-model:value={modelObj[item.bind]}
      autocomplete="off"
      {...nodeProps}
    />
  )
}

/**
 * 生成日期（时间）选择器(无范围)
 */
function renderDatePicker(item, modelObj = {}) {
  const nodeProps = omit(item, ['dialogFormType', 'bind', 'label', 'required', 'format'])
  const showTime = item?.format?.split(' ')[1] ? { format: item?.format?.split(' ')[1] } : false
  return (
    <DatePicker
      style={{ width: '100%' }}
      v-model:value={modelObj[item.bind]}
      valueFormat={item?.format || 'YYYY-MM-DD HH:mm:ss'}
      showTime={showTime}
      format={item?.format || 'YYYY-MM-DD HH:mm:ss'}
      {...nodeProps}
    />
  )
}

/**
 * 生成范围日期（时间）选择器
 */
function renderRangePicker(item, modelObj = {}) {
  const nodeProps = omit(item, ['dialogFormType', 'bind', 'label', 'required', 'format'])
  const showTime = item?.format?.split(' ')[1] ? { format: item?.format?.split(' ')[1] } : false
  return (
    <RangePicker
      style={{ width: '100%' }}
      v-model:value={modelObj[item.bind]}
      valueFormat={item?.format || 'YYYY-MM-DD HH:mm:ss'}
      format={item?.format || 'YYYY-MM-DD HH:mm:ss'}
      showTime={showTime}
      {...nodeProps}
    />
  )
}

/**
 * 生成文件(夹)选择框
 */
function renderPathInput(item, modelObj = {}) {
  const bindKey = item.bind || nanoid()
  let open = false;

  async function handleOpenFileDialog() {
    if (open) return;
    open = true;
    try {
      const filters = (item.filter === '.' || !item?.filter) ? ['*'] : item.filter.split(',')
      const filePaths = await utilsManager.showDialog({
        file_type: item.selectType,
        filters,
        defaultPath: item?.defaultPath,
        multiple: item.isMultiple,
      })
      const filePath = filePaths.join(',')
      filePath && (modelObj[bindKey] = filePath)
    } finally {
      open = false;
    }
  }

  return (
    <Input
      v-model:value={modelObj[bindKey]}
      placeholder={item?.placeholder}
      defaultValue={item?.selectType === 'folder' ? item?.defaultPath : ''}
      suffix={ <UploadOutlined onClick={handleOpenFileDialog} /> }
    />
  )
}

/**
 * 生成checkbox复选框组
 */
function renderCheckboxGroup(item, modelObj = {}) {
  const nodeProps = omit(item, ['dialogFormType', 'bind', 'label', 'required', 'options'])
  const verticalStyle = 'display: flex;flex-direction: column;'
  return (
    <Checkbox.Group
      v-model:value={modelObj[item.bind]}
      style={`${item.direction === 'vertical' ? verticalStyle : ''}`}
      {...nodeProps}
    >
      {
        item.options.map((i) => {
          if (!i?.label) {
            return (
              <Checkbox value={i.rId}>
                {
                  i.value.value.map((it) => {
                    return (it.type === 'var' ? <Tag style="margin-right: 0;">{it.value}</Tag> : it.value)
                  })
                }
              </Checkbox>
            )
          }
          return <Checkbox value={i.value}>{i.label}</Checkbox>
        })
      }
    </Checkbox.Group>
  )
}
/**
 * 生成radio单选框组
 */
function renderRadioGroup(item, modelObj = {}) {
  const nodeProps = omit(item, ['dialogFormType', 'bind', 'label', 'required', 'options'])
  const verticalStyle = 'display: flex;flex-direction: column;'
  return (
    <Radio.Group
      v-model:value={modelObj[item.bind]}
      style={`${item.direction === 'vertical' ? verticalStyle : ''}`}
      {...nodeProps}
    >
      {
        item.options.map((i) => {
          if (!i?.label) {
            return (
              <Radio value={i.rId}>
                {
                  i.value.value.map((it) => {
                    return (it.type === 'var' ? <Tag style="margin-right: 0;">{it.value}</Tag> : it.value)
                  })
                }
              </Radio>
            )
          }
          return <Radio value={i.value}>{i.label}</Radio>
        })
      }
    </Radio.Group>
  )
}
/**
 * 生成select下拉框：单选
 */
function renderSingleSelect(item, modelObj = {}) {
  return renderSelect(item, modelObj, null)
}
/**
 * 生成select下拉框：多选
 */
function renderMultiSelect(item, modelObj = {}) {
  return renderSelect(item, modelObj, 'multiple')
}
function renderSelect(item, modelObj = {}, mode) {
  const nodeProps = omit(item, [
    'dialogFormType',
    'bind',
    'label',
    'style',
    'required',
    'options',
  ])
  
  return (
    <Select
      mode={mode}
      v-model:value={modelObj[item.bind]}
      style={item.style ? item.style : 'min-width: 150px;'}
      placement="bottomRight"
      {...nodeProps}
    >
      {
        item.options.map((i) => {
          if (!i?.label) {
            return (
              <Select.Option value={i.rId}>
                {
                  i.value.value.map((it) => {
                    return (it.type === 'var' ? <Tag style="margin-right: 0;">{it.value}</Tag> : it.value)
                  })
                }
              </Select.Option>
            )
          }
          return <Select.Option value={i.value}>{i.label}</Select.Option>
        })
      }
    </Select>
  )
}

/**
 * 生成文本描述区
 */
function renderTextDesc(item) {
  const finalFontFamily = fontFamilyMap[item.fontFamily || 'msyh']
  const finalFontStyle = item.fontStyle.map(style => fontStyleMap[style]).join(';')

  return (
    <p
      style={`font-size: ${item.fontSize}px;${finalFontFamily};${finalFontStyle}`}
    >
      { item.textContent || '' }
    </p>
  )
}

function renderMessageContent(item) {
  const MESSAGE_ICON_CONFIG = {
    question: <QuestionCircleOutlined class="text-green" style="font-size: 20px;" />,
    error: <CloseCircleOutlined class="text-error" style="font-size: 20px;" />,
    warning: <ExclamationCircleOutlined class="text-warning" style="font-size: 20px;" />,
    message: <InfoCircleOutlined class="text-primary" style="font-size: 20px;" />,
  }
  return (
    <div class="flex justify-start items-center">
      { MESSAGE_ICON_CONFIG[item.messageType] }
      <div style="margin: 0 14px;">
        {
          Array.isArray(item.messageContent)
            ? item.messageContent.map((i) => {
                return (i.type === 'var' ? <Tag style="margin-right: 0;">{i.value}</Tag> : i.value)
              })
            : (item.messageContent || '')
        }
      </div>
    </div>
  )
}

export const createUserFormItem = {
  INPUT: renderInput,
  PASSWORD: renderPassword,
  DATEPICKER: renderDatePicker,
  RANGERPICKER: renderRangePicker,
  PATH_INPUT: renderPathInput,
  CHECKBOX_GROUP: renderCheckboxGroup,
  RADIO_GROUP: renderRadioGroup,
  SINGLE_SELECT: renderSingleSelect,
  MULTI_SELECT: renderMultiSelect,
  TEXT_DESC: renderTextDesc,
  MESSAGE_CONTENT: renderMessageContent,
}
