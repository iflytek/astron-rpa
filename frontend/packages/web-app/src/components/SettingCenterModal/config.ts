import type { Component } from 'vue'

import About from './components/about.vue'
import ApiKeyManage from './components/apiKeyManage/index.vue'
import CommonSetting from './components/commonSetting/index.vue'
// import MsgNotify from './components/msgNotify.vue'
import PluginInstall from './components/pluginInstall/index.vue'
import ShortCut from './components/shortCut/index.vue'
import VideoSetting from './components/videoSetting.vue'

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
    key: 'about',
    icon: 'info',
    name: 'about',
    component: About,
  },
]

export const videoRunOption = [
  {
    label: '每次运行',
    value: 'always',
  },
  {
    label: '运行失败',
    value: 'fail',
  },
]

export const videoTimeOption = [
  {
    label: '最后30秒',
    value: 30,
  },
  {
    label: '最后1分钟',
    value: 60,
  },
  {
    label: '最后5分钟',
    value: 300,
  },
  {
    label: '最后10分钟',
    value: 600,
  },
  {
    label: '最后30分钟',
    value: 1800,
  },
  {
    label: '全部',
    value: 0,
  },
]
