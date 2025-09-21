import { CloseCircleOutlined, ExclamationCircleOutlined, InfoCircleOutlined, QuestionCircleOutlined, UploadOutlined } from '@ant-design/icons-vue'
import { Checkbox, DatePicker, Input, Radio, RangePicker, Select, Tag } from 'ant-design-vue'

import { utilsManager } from '@/platform'

import TagInputUser from '../components/tagInputUser.vue'
import { fontFamilyMap, fontStyleMap } from '../config'

export default function useUserFormItem() {
  // 删除对象属性
  function delObjProperty(obj, delArrs) {
    delArrs.forEach((item) => {
      delete obj[item]
    })
  }
  /**
   * 生成输入框
   */
  function renderInput(item, modelObj) {
    const nodeProps = { ...item }
    delObjProperty(nodeProps, ['dialogFormType', 'bind', 'label', 'required'])
    if (Array.isArray(item?.defaultValue)) { // 处理变量预览的情况
      return <TagInputUser itemData={item} />
    }
    return (
      <Input
        v-model:value={modelObj[item.bind]}
        placeholder={item?.placeholder}
        defaultValue={item?.defaultValue}
        allowClear
        autocomplete="off"
        {...nodeProps}
      />
    )
  }
  /**
   * 生成密码框
   */
  function renderPassword(item, modelObj) {
    const nodeProps = { ...item }
    delObjProperty(nodeProps, ['dialogFormType', 'bind', 'label', 'required'])
    return (
      <Input.Password
        v-model:value={modelObj[item.bind]}
        placeholder={item?.placeholder}
        defaultValue={item?.defaultValue}
        autocomplete="off"
        {...nodeProps}
      />
    )
  }
  /**
   * 生成日期（时间）选择器(无范围)
   */
  function renderDatePicker(item, modelObj) {
    const nodeProps = { ...item }
    delObjProperty(nodeProps, ['dialogFormType', 'bind', 'label', 'required'])
    const showTime = item?.format?.split(' ')[1] ? { format: item?.format?.split(' ')[1] } : false
    return (
      modelObj && (
        <DatePicker
          style={{ width: '100%' }}
          v-model:value={modelObj[item.bind]}
          valueFormat={item?.format || 'YYYY-MM-DD HH:mm:ss'}
          format={item?.format || 'YYYY-MM-DD HH:mm:ss'}
          showTime={showTime}
          placeholder={item?.placeholder}
          defaultValue={item?.defaultValue}
          {...nodeProps}
        />
      )
    )
  }
  /**
   * 生成范围日期（时间）选择器
   */
  function renderRangePicker(item, modelObj) {
    const nodeProps = { ...item }
    delObjProperty(nodeProps, ['dialogFormType', 'bind', 'label', 'required'])
    const showTime = item?.format?.split(' ')[1] ? { format: item?.format?.split(' ')[1] } : false
    return (
      modelObj && (
        <RangePicker
          style={{ width: '100%' }}
          v-model:value={modelObj[item.bind]}
          valueFormat={item?.format || 'YYYY-MM-DD HH:mm:ss'}
          format={item?.format || 'YYYY-MM-DD HH:mm:ss'}
          showTime={showTime}
          placeholder={item?.placeholder}
          defaultValue={item?.defaultValue}
          {...nodeProps}
        />
      )
    )
  }
  /**
   * 生成文件(夹)选择框
   */
  function renderPathInput(item, modelObj) {
    console.log('item, modelObj', item, modelObj)
    function handleOpenFileDialog(item, modelObj) {
      const filters = (item.filter === '.' || !item?.filter) ? ['*'] : item.filter.split(',')
      utilsManager.showDialog({
        file_type: item.selectType,
        filters,
        defaultPath: item?.defaultPath,
        multiple: item.isMultiple,
      }).then((res) => {
        console.log(res)
        if (res) {
          let strVal = ''
          if (Array.isArray(res)) {
            res.forEach((item) => {
              strVal += `${item},`
            })
          }
          else {
            strVal = `${res}`
          }
          modelObj[item.bind] = strVal
        }
      })
    }
    const nodeProps = { ...item }
    delObjProperty(nodeProps, ['dialogFormType', 'label', 'required'])
    return (
      modelObj && (
        <Input
          v-model:value={modelObj[item.bind]}
          placeholder={item?.placeholder}
          defaultValue={item?.selectType === 'folder' ? item?.defaultPath : ''}
          suffix={
            <UploadOutlined onClick={() => { handleOpenFileDialog(item, modelObj) }} />
          }
        />
      )
    )
  }

  /**
   * 生成checkbox复选框组
   */
  function renderCheckboxGroup(item, modelObj) {
    const nodeProps = Object.assign({}, item)
    delObjProperty(nodeProps, ['dialogFormType', 'bind', 'label', 'required', 'options'])
    const verticalStyle = 'display: flex;flex-direction: column;'
    return (
      modelObj && (
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
    )
  }
  /**
   * 生成radio单选框组
   */
  function renderRadioGroup(item, modelObj) {
    const nodeProps = Object.assign({}, item)
    delObjProperty(nodeProps, ['dialogFormType', 'bind', 'label', 'required', 'options'])
    const verticalStyle = 'display: flex;flex-direction: column;'
    return (
      modelObj && (
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
    )
  }
  /**
   * 生成select下拉框：单选
   */
  function renderSingleSelect(item, modelObj) {
    return renderSelect(item, modelObj, null)
  }
  /**
   * 生成select下拉框：多选
   */
  function renderMultiSelect(item, modelObj) {
    return renderSelect(item, modelObj, 'multiple')
  }
  function renderSelect(item, modelObj, mode) {
    const nodeProps = { ...item }
    delObjProperty(nodeProps, [
      'dialogFormType',
      'bind',
      'label',
      'style',
      'required',
      'options',
    ])
    return (
      modelObj && (
        <Select
          mode={mode}
          v-model:value={modelObj[item.bind]}
          placeholder={item?.placeholder}
          style={`${item.style ? item.style : 'min-width: 150px;'}`}
          getPopupContainer={triggerNode => triggerNode.parentNode}
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
      question: <QuestionCircleOutlined style="color: #52c41a;font-size: 28px;" />,
      error: <CloseCircleOutlined style="color: #f5222d;font-size: 28px;" />,
      warning: <ExclamationCircleOutlined style="color: #faad14;font-size: 28px;" />,
      message: <InfoCircleOutlined style="color: #1890ff;font-size: 28px;" />,
    }
    return (
      <div style="display: flex; justify-content: flex-start; align-items: center;">
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

  return {
    delObjProperty,
    createItemFn: {
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
    },
  }
}
