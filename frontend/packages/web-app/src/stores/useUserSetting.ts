import type { BasicColorSchema } from '@vueuse/core'
import { message } from 'ant-design-vue'
import deepmerge from 'deepmerge'
import { defineStore } from 'pinia'
import { computed, shallowRef, toRaw } from 'vue'
import { get, isNil } from 'lodash-es'

import i18next from '@/plugins/i18next'
import { autoStartDisable, autoStartEnable, autoStartStatus } from '@/api/setting'
import { utilsManager } from '@/platform'

export type Theme = BasicColorSchema

export const DEFAULT_FORM: RPA.VideoFormMap = {
  saveType: true,
  enable: false,
  scene: 'fail',
  cutTime: 30,
  fileClearTime: 7,
  // maxRecordingTime: 10,
  filePath: '',
}

const useUserSettingStore = defineStore('useUserSetting', () => {
  const userSetting = shallowRef<RPA.UserSetting>({
    commonSetting: { // 常规设置
      startupSettings: false, // 启动项设置 - 引擎接口获取存储，true 开启自启动，false-关闭开机自启动
      closeMainPage: false, // true-最小化托盘  false-退出应用
      hideLogWindow: false, // 运行时的右下角日志窗口 true-开启隐藏  false-关闭隐藏
      hideDetailLogWindow: false, // 运行完的详细日志窗口 true-开启隐藏  false-关闭隐藏
      autoSave: true, // 自动保存 true-开启  false-关闭
      theme: 'auto',
    },
    shortcutConfig: {}, // 快捷键设置
    videoForm: DEFAULT_FORM, // 录屏设置
    msgNotifyForm: {}, // 消息通知设置
    language: i18next.language,
    version: '',
    platform: '',
  })

  async function setLanguageSetting(lng: string) {
    await Promise.all([
      saveUserSetting({ language: lng }),
      i18next.changeLanguage(lng),
    ])
  }

  // 获取常规设置
  const getSetting = async () => {
    const [autostart, setting] = await Promise.all([
      autoStartStatus(),
      utilsManager.getUserSetting(),
    ])

    userSetting.value = deepmerge.all<RPA.UserSetting>([
      userSetting.value,
      setting,
      { commonSetting: { startupSettings: autostart } } as RPA.UserSetting,
    ])

    const serverLanguage = get(setting, 'language');
    if (isNil(serverLanguage)) {
      utilsManager.saveUserSetting(toRaw(userSetting.value))
    }
  }

  const saveUserSetting = async (params: Partial<RPA.UserSetting>) => {
    userSetting.value = {
      ...userSetting.value,
      ...params,
    }
    // TODO: 直接把响应式对象穿进去，通过 electron IPC 通信时有问题，先通过这种方式临时转成普通对象
    await utilsManager.saveUserSetting(JSON.parse(JSON.stringify(userSetting.value)))
  }

  // 修改常规设置
  const changeCommonConfig = async (key: string, value: boolean) => {
    if (key === 'startupSettings') {
      const func = value ? autoStartEnable : autoStartDisable
      const res = await func()
      message.success(res.data.tips)
      getSetting()

      return
    }

    saveUserSetting({
      commonSetting: {
        ...userSetting.value.commonSetting,
        [key]: value,
      },
    })
  }

  // 运行结束后是否打开日志弹窗
  const openLogModalAfterRun = computed(() => !userSetting.value.commonSetting.hideDetailLogWindow)

  getSetting()

  return {
    userSetting,
    openLogModalAfterRun,
    saveUserSetting,
    changeCommonConfig,
    setLanguageSetting,
  }
})

export default useUserSettingStore
