import type { Component } from 'vue'

import About from './components/about.vue'
import ApiKeyManage from './components/apiKeyManage/index.vue'
import CommonSetting from './components/commonSetting/index.vue'
// import MsgNotify from './components/msgNotify.vue'
import PluginInstall from './components/pluginInstall/index.vue'
import ShortCut from './components/shortCut/index.vue'
import VideoSetting from './components/videoSetting.vue'
import Voucher from './components/voucher/index.vue'

export interface MenuItem {
  key: string
  icon: string
  name: string
  component: Component
}

// 设置中心左侧菜单项配置数据
export const menuConfig: MenuItem[] = [
  {
    key: 'pluginInstall',
    icon: 'plugin',
    name: 'pluginInstallation',
    component: PluginInstall,
  },
  {
    key: 'commonSetting',
    icon: 'setting-1',
    name: 'generalSettings',
    component: CommonSetting,
  },
  {
    key: 'videoSetting',
    icon: 'video',
    name: 'runRecording',
    component: VideoSetting,
  },
  // {
  //   key: 'msgNotify',
  //   icon: 'message',
  //   name: 'notification',
  //   component: MsgNotify,
  // },
  {
    key: 'shortcut',
    icon: 'shortcut-key',
    name: 'shortcutKey',
    component: ShortCut,
  },
  {
    key: 'apiKey',
    icon: 'api-key',
    name: 'apiKeyMg',
    component: ApiKeyManage,
  },
  {
    key: 'voucher',
    icon: 'approval',
    name: 'voucher',
    component: Voucher,
  },
  {
    key: 'about',
    icon: 'info',
    name: 'about',
    component: About,
  },
]

export const videoRunOption = [
  {
    label: 'settingCenter.runRecord.always',
    value: 'always',
  },
  {
    label: 'settingCenter.runRecord.onFail',
    value: 'fail',
  },
]

export const videoTimeOption = [
  {
    label: 'settingCenter.runRecord.last30s',
    value: 30,
  },
  {
    label: 'settingCenter.runRecord.last1m',
    value: 60,
  },
  {
    label: 'settingCenter.runRecord.last5m',
    value: 300,
  },
  {
    label: 'settingCenter.runRecord.last10m',
    value: 600,
  },
  {
    label: 'settingCenter.runRecord.last30m',
    value: 1800,
  },
  {
    label: 'settingCenter.runRecord.all',
    value: 0,
  },
]
