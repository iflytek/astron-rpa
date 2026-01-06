import { Button, message } from 'ant-design-vue'
import { ref } from 'vue'

import type { AnyObj } from '@/types/common'
import type { DialogOption } from '@/views/Arrange/components/customDialog/types'

export default function useUserFormDialog(option: DialogOption, onClose: () => void, onSave?: (data: AnyObj) => void) {
  // 定义表单引用
  const formRef = ref(null)
  // 定义表单状态
  const formState = ref(option.formModel)

  // 定义自定义对话框数据转换方法
  // const transformCustom = (data: string): DialogOption => {
  //   const { box_title, design_interface, result_button } = JSON.parse(data || '{}')
  //   console.log('design_interface', design_interface)
  //   const { mode = 'window', buttonType = 'confirm_cancel', formList = [] } = JSON.parse(design_interface || '{}')
  //   console.log('formList', formList)
  //   const formModel = { result_button } as AnyObj
  //   const itemList = formList?.map((item) => {
  //     const { configKeys, dialogFormType } = item
  //     const res = { dialogFormType } as FormItemConfig
  //     configKeys.forEach((key) => {
  //       if (key === 'options') {
  //         res[key] = item[key].value?.map((op) => {
  //           // const { rId, value } = op
  //           return {
  //             label: op.value,
  //             value: op.value,
  //           }
  //         })
  //       }
  //       else {
  //         // eslint-disable-next-line no-prototype-builtins
  //         res[key] = item[key]?.hasOwnProperty('value') ? item[key]?.value : item[key]
  //       }
  //     })
  //     if (configKeys.includes('options') && configKeys.includes('defaultValue')) {
  //       res.defaultValue = item.options.value.find(op => op.rId === res.defaultValue)?.value || item.defaultValue.defualt
  //     }
  //     if (dialogFormType !== 'TEXT_DESC') {
  //       formModel[res.bind] = res?.defaultValue || res?.defaultPath
  //     }
  //     const result = JSON.parse(JSON.stringify(res)) // 过滤掉值为undefined的字段
  //     if (dialogFormType === 'PASSWORD') { // 密码框统一加上长度校验
  //       result.rules = getPasswordRules(result.label)
  //     }
  //     return result
  //   })
  //   return {
  //     mode,
  //     title: box_title || '自定义对话框',
  //     buttonType,
  //     itemList,
  //     formModel,
  //   }
  // }

  const handleClose = () => {
    if (option.mode !== 'modal') {
      // 自定义对话框点击×关闭时才需要输出{ result_button: 'cancel' }
      onSave?.({ result_button: 'cancel' })
    }

    onClose()
  }

  const handleBtns = (btnOpt: string) => {
    console.log('handleBtns', btnOpt)
    console.log('option', option)

    // 只要是预览弹窗没有任何业务逻辑直接关闭
    if (option.mode !== 'modal') {
      const itemList = option.itemList
      if (itemList.length === 1 && itemList[0].dialogFormType === 'MESSAGE_CONTENT') {
        formState.value[itemList[0].bind] = btnOpt
        onSave?.(formState.value)
      }
      else if (btnOpt === 'confirm') {
        formRef.value.validate()
          .then(() => {
            formState.value.result_button = btnOpt
            onSave?.(formState.value)
          })
          .catch(() => {
            message.warning('请检查表单内容')
          })
      }
      else if (btnOpt === 'cancel') {
        onSave?.({ result_button: 'cancel' })
      }
    }

    onClose()
  }

  const renderFooterBtns = (buttonType: string) => {
    console.log('renderFooterBtns', buttonType)

    const buttons = {
      confirm: <Button type="primary" onClick={() => handleBtns('confirm')}>确定</Button>,
      cancel: <Button onClick={() => handleBtns('cancel')}>取消</Button>,
      yes: <Button type="primary" onClick={() => handleBtns('yes')}>是</Button>,
      no: <Button onClick={() => handleBtns('no')}>否</Button>,
    }

    return (
      <>
        {buttonType.split('_').reverse().map(item => buttons[item])}
      </>
    )
  }

  return {
    formRef,
    formState,
    handleClose,
    renderFooterBtns,
  }
}
