// 智能组件拾取窗口通信事件
export enum SMART_COMP_PICK_EVENT {
  SHOW_MENU = 'show-menu', // 显示菜单
  HIDE_MENU = 'hide-menu', // 隐藏菜单
  PAUSE_PICK = 'pause-pick', // 暂停拾取
  RESUME_PICK = 'resume-pick', // 恢复拾取
  ZOOM_IN = 'zoom-in', // 放大选区
  ZOOM_OUT = 'zoom-out', // 缩小选区
  CONFIRM = 'confirm', // 确认
  CANCEL = 'cancel', // 取消
  SHOW_ERROR_DIALOG = 'show-error-dialog', // 显示错误对话框
  ERROR_DIALOG_CONFIRM = 'error-dialog-confirm', // 错误对话框确认
}
