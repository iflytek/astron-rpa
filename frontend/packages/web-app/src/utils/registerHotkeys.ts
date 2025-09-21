import hotkeys from 'hotkeys-js'
import { cloneDeep } from 'lodash-es'
import { ref } from 'vue'

import { getUserSetting } from '@/api/setting'
import { SCOPE, shortcuts } from '@/constants/shortcuts'

const hotkeySetting = ref(cloneDeep(shortcuts))
const hotkeyFnMap = ref({}) // 已注册快捷键的回调函数

// // 注销所有快捷键
// const unregisterAll = () => {
//   Object.keys(hotkeyFnMap.value).forEach(id=>{
//     const hotkey = hotkeySetting.value[id].text.replace(/\s/g, "")
//     hotkeys.unbind(hotkey)
//   })
// }

// // 注册快捷键
// const registerAll = () => {
//   Object.keys(hotkeyFnMap.value).forEach(id=>{
//     const hotkey = hotkeySetting.value[id].text.replace(/\s/g, "")
//     hotkeys(hotkey, hotkeyFnMap[id])
//   })
// }

function getHotkeySetting(autoRegister = false) {
  getUserSetting().then((res: any) => {
    if (res) {
      const localShortcuts = res.shortcutConfig || {}
      Object.keys(hotkeySetting.value).forEach((key) => {
        const currentItem = hotkeySetting.value[key]
        const localItem = localShortcuts[key]
        if (localItem) {
          // 注销快捷键
          if (autoRegister && hotkeyFnMap[currentItem.id] && localItem.value !== currentItem.value) {
            const oldHotkey = currentItem.text.replace(/\s/g, '')
            hotkeys.unbind(oldHotkey)
            const hotkey = localItem.text.replace(/\s/g, '')
            hotkeys(hotkey, SCOPE, hotkeyFnMap[currentItem.id])
          }
          // 存在本地数据即可覆盖数据
          currentItem.value = localItem.value
          currentItem.text = localItem.text
        }
      })
    }
  })
}

// 初始化快捷键设置
getHotkeySetting()

// 更新快捷键设置
function updateHotkeysSetting() {
  hotkeys.setScope(SCOPE)
  getHotkeySetting(true)
}

hotkeys.setScope(SCOPE)

// 注册单个快捷键
function registerHotkey(id: string, callback: () => void) {
  if (!hotkeySetting.value[id].value) {
    return console.error(`未找到快捷键配置：${id}, 请在config文件夹下新增快捷键配置`)
  }
  hotkeyFnMap[id] = callback
  const hotkey = hotkeySetting.value[id].text.replace(/\s/g, '')
  hotkeys(hotkey, SCOPE, () => {
    hotkeyFnMap[id]()
  })
}

// 注销单个快捷键
function unregisterHotkey(id: string) {
  if (!hotkeySetting.value[id].value) {
    return console.error(`未找到快捷键配置：${id}, 请在config文件夹下新增快捷键配置`)
  }
  delete hotkeyFnMap[id]
  const hotkey = hotkeySetting.value[id].text.replace(/\s/g, '')
  hotkeys.unbind(hotkey, SCOPE)
}

export {
  registerHotkey,
  unregisterHotkey,
  updateHotkeysSetting,
}
