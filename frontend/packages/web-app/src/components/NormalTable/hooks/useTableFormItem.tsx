import { CloseOutlined, DownOutlined } from '@ant-design/icons-vue'
import { Button, DatePicker, Dropdown, Input, Menu, Select, Space } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import FilterComp from '@/components/FilterComp/FilterComp.vue'

export default function useTableFormItem() {
  const { t } = useTranslation()

  // 删除对象属性
  function delObjProperty(obj, delArrs) {
    delArrs.forEach((item) => {
      delete obj[item]
    })
  }

  /**
   * 生成input
   */
  function renderInput(item, modelObj, searchFn) {
    const { placeholder, ...nodeProps } = item
    delObjProperty(nodeProps, ['componentType', 'bind', 'label'])
    const isHidden = item.hidden ? 'hide' : ''

    if (!modelObj)
      return null

    if (item.isTrim) {
      return (
        <Input
          class={isHidden}
          placeholder={
            placeholder
              ? t(placeholder)
              : t('common.enterPlaceholder', { name: t(item.label) })
          }
          allowClear
          style="width: 200px;"
          {...nodeProps}
          onClick={() => item.clickFn?.()}
          onChange={() => searchFn()}
        />
      )
    }

    return (
      <Input
        class={isHidden}
        v-model:value={modelObj[item.bind]}
        placeholder={
          placeholder
            ? t(placeholder)
            : t('common.enterPlaceholder', { name: t(item.label) })
        }
        allowClear
        style="width: 200px;"
        {...nodeProps}
        onClick={() => item.clickFn?.()}
        onChange={() => searchFn()}
      />
    )
  }
  /**
   * 生成select下拉框
   */
  function renderSelect(item, modelObj, searchFn) {
    const { placeholder, ...nodeProps } = item

    delObjProperty(nodeProps, [
      'componentType',
      'bind',
      'label',
      'options',
      'labelKey',
      'valueKey',
      'disabledKey',
      'style',
    ])

    const labelKey = item.labelKey || ''
    const valueKey = item.valueKey || ''
    const disabledKey = item.disabledKey || ''

    return (
      modelObj && (
        <Select
          v-model:value={modelObj[item.bind]}
          placeholder={
            placeholder
              ? t(placeholder)
              : t('common.selectPlaceholder', { name: t(item.label) })
          }
          style={`${item.style ? item.style : 'min-width: 150px;'}`}
          {...nodeProps}
          onChange={() => {
            searchFn()
          }}
        >
          {item.options?.map(info => (
            <Select.Option
              value={!valueKey ? info.value : info[valueKey]}
              disabled={!disabledKey ? info.disabled : info[disabledKey]}
            >
              {!labelKey ? t(info.label) : info[labelKey]}
            </Select.Option>
          ))}
        </Select>
      )
    )
  }

  /**
   * 生成日期（时间）范围选择器
   */
  function renderDatePicker(item, modelObj, searchFn) {
    const { placeholder, ...nodeProps } = item

    delObjProperty(nodeProps, ['componentType', 'bind', 'label'])

    return (
      modelObj && (
        <DatePicker.RangePicker
          placeholder={placeholder ? t(placeholder) : undefined}
          v-model:value={modelObj[item.bind]}
          {...nodeProps}
          onChange={() => searchFn()}
        />
      )
    )
  }

  /**
   * 生成按钮
   */
  function renderButton(item) {
    const nodeProps = { ...item }
    delObjProperty(nodeProps, [
      'btnType',
      'label',
      'action',
      'clickFn',
      'options',
    ])
    const { btnType, label, clickFn, options } = item
    const isHidden = (item.class || '') + (item.hidden ? 'hide' : '')
    const isDanger = item.danger === true

    if (btnType !== 'dropdown') {
      return (
        <Button
          danger={isDanger}
          class={`singleBtn ${isHidden}`}
          {...nodeProps}
          onClick={clickFn}
        >
          {t(label)}
        </Button>
      )
    }

    return (
      <Dropdown
        class={isHidden}
        overlay={(
          <Menu>
            {options.map(op => (
              <Menu.Item key={op.key} onClick={op.clickFn}>
                {t(op.label)}
              </Menu.Item>
            ))}
          </Menu>
        )}
      >
        <Button class="dropdownBtn">
          <Space>
            {t(label)}
            <DownOutlined />
          </Space>
        </Button>
      </Dropdown>
    )
  }
  /**
   * 生成dropdown
   */
  // function renderDropdown(item, btnClick, dataItem) {
  //   const nodeProps = Object.assign({}, item)
  //   delObjProperty(nodeProps, ['componentType', 'label', 'func'])
  //   return (
  //     <Dropdown onCommand={(command) => item.itemFunc?.(command, dataItem) || btnClick?.(command, dataItem)} v-slots={{
  //       dropdown: () => {
  //         return (
  //           <Dropdown-menu>{
  //             item.options?.map((info) => {
  //               const infoProps = Object.assign({}, info)
  //               delete infoProps.label
  //               return <Dropdown-item {...info}>{info.label}</Dropdown-item>
  //             })
  //           }</Dropdown-menu>
  //         )
  //       },
  //       default: () => {
  //         return item.defaultSlot?.()
  //       }
  //     }}>
  //       <Button {...nodeProps}>
  //         {item.label}
  //         <el-icon class="el-icon--right">
  //           {item.icon || <ArrowDown />}
  //         </el-icon>
  //       </Button>
  //     </Dropdown>
  //   )
  // }

  /**
   * 生成按钮组合
   */
  // function renderButtonList(list, btnClick, data) {
  //   const btnList = list.filter((info) => !info.hidden)
  //   const length = btnList?.length || 0
  //   const buttonList = (length > 3 ? btnList?.slice(0, 2) : btnList)
  //   const moreButton = (length > 3 ? btnList?.slice(2, length) : [])// 更多下面的隐藏button
  //   moreButton?.forEach((item) => {
  //     item.command = item.func
  //   })
  //   const dotIcon = {
  //     defaultSlot: () => {
  //       return (
  //         <el-icon class="pointer color-primary">
  //           <MoreFilled />
  //         </el-icon>
  //       )
  //     },
  //     options: moreButton
  //   }
  //   const renderDot = () => {
  //     return length > 3 && renderDropdown(dotIcon, btnClick, data)
  //   }
  //   return (
  //     <div class="n-operate">
  //       {
  //         buttonList?.map((info) => {
  //           return renderButton(info, btnClick, data)
  //         })
  //       }
  //       {
  //         renderDot()
  //       }
  //     </div>
  //   )
  // }

  /**
   * 生成cascader级联
   */
  // function renderCascader(item, modelObj) {
  //   const nodeProps = Object.assign({}, item)
  //   delObjProperty(nodeProps, ['componentType', 'bind', 'label', 'options', 'itemFunc'])
  //   return (
  //     modelObj && (
  //       <el-cascader v-model={modelObj[item.bind]} onChange={(val) => item.itemFunc?.(val)} options={item.options}
  //         placeholder={`请选择${item.label}`} {...nodeProps} />
  //     )
  //   )
  // }
  /**
   * 生成treeselect树形选择器
   */
  // function renderTreeSelect(item, modelObj) {
  //   const nodeProps = Object.assign({}, item)
  //   delObjProperty(nodeProps, ['componentType', 'bind', 'label', 'itemFunc', 'load'])
  //   return (
  //     modelObj && (
  //         <el-tree-select v-model={modelObj[item.bind]} data={item.data} nodeKey="id" placeholder={`请选择${item.label}`} {...nodeProps}
  //           onNodeClick={(val, node) => {
  //             // console.log(val[item.props.value || 'id'])
  //             if (!item.showCheckbox && !node.disabled) {
  //               modelObj[item.bind] = val[item.props.value || 'id']
  //             }
  //           }}
  //           onCheck={(val) => {
  //             if (item.showCheckbox) {
  //               modelObj[item.bind].push(val[item.props.value || 'id'])
  //             }
  //           }}
  //           load={(node, resolve) => {
  //             setTimeout(() => {
  //               resolve(item.load?.(node))
  //             }, 400)
  //           }} />
  //     )
  //   )
  // }
  /**
   * 生成checkbox复选框
   */
  // function renderCheckbox(item, modelObj) {
  //   const nodeProps = Object.assign({}, item)
  //   delObjProperty(nodeProps, ['componentType', 'bind', 'label', 'options', 'labelKey', 'valueKey'])
  //   const labelKey = item.labelKey || ''
  //   const valueKey = item.valueKey || ''
  //   return (
  //     modelObj && (
  //       <Checkbox-group v-model={modelObj[item.bind]} {...nodeProps}>
  //         {
  //           item.options?.map((info) => {
  //             return (
  //               <Checkbox label={!labelKey ? info.name : info[labelKey]} name={!valueKey ? info.id : info[valueKey]} disabled={item.disabled} {...info} />
  //             )
  //           })
  //         }
  //       </Checkbox-group>
  //     )
  //   )
  // }

  /**
   * renderBack 返回按钮
   */
  function renderBack(item) {
    return <CloseOutlined class="back-btn" onClick={() => item.backFn} />
  }

  /**
   * renderFilter 过滤组件
   */
  function renderFilter(item, modelObj, searchFn) {
    return (
      <div class="filter-comp">
        <FilterComp
          filterGroups={item.filterGroups}
          placement={item.placement}
          reset={item.reset}
          v-model={modelObj[item.bind]}
          onFilterChange={() => searchFn}
        />
      </div>
    )
  }

  return {
    delObjProperty,
    createHomeForm: {
      input: renderInput,
      select: renderSelect,
      datePicker: renderDatePicker,
      button: renderButton,
      back: renderBack, // 返回按钮
      filter: renderFilter, // 过滤组件
      // dropdown: renderDropdown,
      // buttonList: renderButtonList,
      // treeSelect: renderTreeSelect,
    },
  }
}
