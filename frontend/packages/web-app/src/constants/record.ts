export enum RecordActionType {
  GET_ELEMENT_INFO = 'get-element-info',
  GET_ELEMENT_TEXT = 'get-element-text',
  GET_ELEMENT_CODE = 'get-element-code',
  GET_ELEMENT_LINK = 'get-element-link',
  GET_ELEMENT_ATTR = 'get-element-attr',
  INPUT = 'input',
  MOUSE_MOVE = 'mouse-move',
  CLICK = 'click',
  CLICK_LEFT = 'click-left',
  CLICK_LEFT_RIGHT = 'click-left-right',
  CLICK_RIGHT = 'click-right',
  WAIT_ELEMENT = 'wait-element',
  WAIT_ELEMENT_SHOW = 'wait-element-show',
  WAIT_ELEMENT_HIDE = 'wait-element-hide',
  SNAPSHOT = 'snapshot',
}

// 网页操作
export const WebRecordActionType: Partial<Record<RecordActionType, string>> = {
  [RecordActionType.GET_ELEMENT_TEXT]: 'BrowserElement.element_operation',
  [RecordActionType.GET_ELEMENT_CODE]: 'BrowserElement.element_operation',
  [RecordActionType.GET_ELEMENT_LINK]: 'BrowserElement.element_operation',
  [RecordActionType.GET_ELEMENT_ATTR]: 'BrowserElement.element_operation',
  [RecordActionType.INPUT]: 'BrowserElement.input',
  [RecordActionType.MOUSE_MOVE]: 'BrowserElement.hover_over',
  [RecordActionType.CLICK_LEFT]: 'BrowserElement.click',
  [RecordActionType.CLICK_LEFT_RIGHT]: 'BrowserElement.click',
  [RecordActionType.CLICK_RIGHT]: 'BrowserElement.click',
  [RecordActionType.WAIT_ELEMENT_SHOW]: 'BrowserElement.wait_element',
  [RecordActionType.WAIT_ELEMENT_HIDE]: 'BrowserElement.wait_element',
  [RecordActionType.SNAPSHOT]: 'BrowserElement.screenshot',
}

// 桌面操作
export const DesktopRecordActionType: Partial<Record<RecordActionType, string>> = {
  [RecordActionType.GET_ELEMENT_TEXT]: 'WinEle.get_element_text',
  [RecordActionType.INPUT]: 'WinEle.input_text_element',
  [RecordActionType.MOUSE_MOVE]: 'WinEle.hover_element',
  [RecordActionType.CLICK_LEFT]: 'WinEle.click_element',
  [RecordActionType.CLICK_LEFT_RIGHT]: 'WinEle.click_element',
  [RecordActionType.CLICK_RIGHT]: 'WinEle.click_element',
  [RecordActionType.SNAPSHOT]: 'WinEle.screenshot_element',
}

export const RecordActionMap: Record<RecordActionType, { icon: string, label: string }> = {
  [RecordActionType.GET_ELEMENT_INFO]: {
    icon: 'get-element-text-web',
    label: '获取元素信息',
  },
  [RecordActionType.GET_ELEMENT_TEXT]: {
    icon: 'get-element-text-web',
    label: '获取文字内容',
  },
  [RecordActionType.GET_ELEMENT_CODE]: {
    icon: 'get-element-text-web',
    label: '获取源代码',
  },
  [RecordActionType.GET_ELEMENT_LINK]: {
    icon: 'get-element-text-web',
    label: '获取链接地址',
  },
  [RecordActionType.GET_ELEMENT_ATTR]: {
    icon: 'get-element-text-web',
    label: '获取元素属性',
  },
  [RecordActionType.INPUT]: {
    icon: 'fill-input-web',
    label: '输入',
  },
  [RecordActionType.MOUSE_MOVE]: {
    icon: 'mouse-move',
    label: '鼠标移动到这里',
  },
  [RecordActionType.CLICK]: {
    icon: 'click-element-web',
    label: '点击',
  },
  [RecordActionType.CLICK_LEFT]: {
    icon: 'click-element-web',
    label: '点击',
  },
  [RecordActionType.CLICK_LEFT_RIGHT]: {
    icon: 'click-element-web',
    label: '双击',
  },
  [RecordActionType.CLICK_RIGHT]: {
    icon: 'click-element-web',
    label: '右键点击',
  },
  [RecordActionType.WAIT_ELEMENT]: {
    icon: 'wait-element-web',
    label: '等待元素',
  },
  [RecordActionType.WAIT_ELEMENT_SHOW]: {
    icon: 'wait-element-web',
    label: '等待元素出现',
  },
  [RecordActionType.WAIT_ELEMENT_HIDE]: {
    icon: 'wait-element-web',
    label: '等待元素消失',
  },
  [RecordActionType.SNAPSHOT]: {
    icon: 'pick-element-screenshot-web',
    label: '截图',
  },
}

// 窗口通信事件
export enum RECORD_EVENT {
  SHOW_MENU = 'show-menu', // 显示菜单
  HIDE_MENU = 'hide-menu', // 隐藏菜单
  PAUSE_PICK = 'pause-pick', // 暂停拾取
  RESUME_PICK = 'resume-pick', // 恢复拾取
  CLICK_ACTION = 'click-action', // 点击菜单
}
