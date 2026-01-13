import { Button, message } from 'ant-design-vue'
import { ref } from 'vue'

import type { AnyObj } from '@/types/common'
import type { DialogOption } from '@/views/Arrange/components/customDialog/types'

export default function useUserFormDialog(option: DialogOption, onClose: () => void, onSave?: (data: AnyObj) => void) {
  // 定义表单引用
  const formRef = ref(null)
  // 定义表单状态
  const formState = ref(option.formModel)

  const handleClose = () => {
    if (option.mode !== 'modal') {
      // 自定义对话框点击×关闭时才需要输出{ result_button: 'cancel' }
      onSave?.({ result_button: 'cancel' })
    }

    onClose()
  }

  const handleBtns = (btnOpt: string) => {
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
