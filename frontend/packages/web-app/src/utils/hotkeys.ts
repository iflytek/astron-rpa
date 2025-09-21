import hotkeys from 'hotkeys-js'

import { SCOPE } from '@/constants/shortcuts'

let itemScope = ''

function resetKeyboard() {
  if (itemScope) {
    hotkeys.unbind('*', itemScope)
    hotkeys.deleteScope(itemScope)
    hotkeys.setScope(SCOPE)
  }
}

// function isBodyOrAntModal(e: Event): boolean {
//   // 使用类型断言确保 e.target 是 HTMLElement 类型
//   if ((e.target as HTMLElement).tagName === 'BODY') {
//     return true
//   }

//   // 检查 e.target 是否为 SVG 元素并有 className.baseVal，如果是则返回 false
//   // 否则检查 e.target 是否包含 "ant-modal" 类名
//   const target = e.target as HTMLElement | SVGElement
//   if (target instanceof SVGElement && target.className instanceof SVGAnimatedString) {
//     return false
//   }

//   return target.className?.indexOf('ant-modal') > -1
// }

function getKeyboard(data, callback) {
  // 判断传进来的data是否有id属性，没有的话就加上
  if (!(Object.prototype.hasOwnProperty.call(data, 'id') && data.id)) {
    data.id = Date.now().toString(36)
  }
  // 通过setScope设定范围scope
  hotkeys.setScope(data.id)
  itemScope = data.id
  let keyboard = ''
  let keyCodeValue: string | number = ''
  let keyValue = ''

  hotkeys('*', data.id, (e: KeyboardEvent) => {
    // if (isBodyOrAntModal(e)) {
    if (![16, 17, 18, 91].includes(e.keyCode)) {
      const k = e.key === ' ' ? 'space' : e.key
      keyboard = k
      keyCodeValue = e.keyCode
      keyValue = k
      if (e.ctrlKey) {
        // keyCode 17
        keyValue = `Ctrl,${keyboard}`
        keyboard = `Ctrl + ${keyboard}`
        keyCodeValue = `17,${keyCodeValue}`
      }
      if (e.shiftKey) {
        // keyCode 16
        keyValue = `Shift,${keyboard}`
        keyboard = `Shift + ${keyboard}`
        keyCodeValue = `16,${keyCodeValue}`
      }
      if (e.altKey) {
        // keyCode 18
        keyValue = `Alt,${keyboard}`
        keyboard = `Alt + ${keyboard}`
        keyCodeValue = `18,${keyCodeValue}`
      }
      callback({
        id: data.id,
        text: keyboard,
        value: keyValue.replaceAll(' + ', ','),
      })
    }
    // }
  })
}

export {
  getKeyboard,
  resetKeyboard,
}
