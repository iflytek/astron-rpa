import safe360Icon from '@/assets/img/pluginInstall/360.png'
import x360Icon from '@/assets/img/pluginInstall/360x.png'
import edgeIcon from '@/assets/img/pluginInstall/edge-icon.png'
import firefoxIcon from '@/assets/img/pluginInstall/firefox.png'
import googleIcon from '@/assets/img/pluginInstall/google-icon.png'

export interface PLUGIN_ITEM {
  type: BROWER_LIST
  icon: string
  title: string
  isInstall: boolean
  installVersion: string
  description: string
  isNewest?: boolean
  oparateStepImgs?: string[]
  stepDescription?: string[]
  loading?: boolean
}

export enum BROWER_LIST {
  'CHROME' = 'chrome',
  'EDGE' = 'microsoft_edge',
  'FIREFOX' = 'firefox',
  '360SE' = '360',
  '360X' = '360x',
}

// 插件列表配置
export const BROWER_PLUGIN_LIST: PLUGIN_ITEM[] = [
  {
    type: BROWER_LIST.CHROME, // chrome扩展程序
    icon: googleIcon,
    title: 'chrome',
    isInstall: false,
    installVersion: '',
    description: 'chromeDescription',
    isNewest: true,
    stepDescription: ['插件已经安装，根据以下图片步骤开启浏览器插件', '若安装失败，请打开插件路径拖动加载插件'], // 安装后手动操作的步骤描述
    oparateStepImgs: ['chrome1.jpg', 'chrome2.jpg'], // 安装后手动操作的步骤图片
    loading: false, // 是否正在安装
  },
  {
    type: BROWER_LIST.EDGE, // edge扩展程序
    icon: edgeIcon,
    title: 'edge',
    isInstall: false,
    installVersion: '',
    description: 'edgeDescription',
    isNewest: true,
    stepDescription: ['插件已经安装，根据以下图片步骤开启浏览器插件', '若安装失败，请打开插件路径拖动加载插件'], // 安装后手动操作的步骤描述
    oparateStepImgs: ['edge1.jpg', 'edge2.jpg'], // 安装后手动操作的步骤图片
    loading: false, // 是否正在安装
  },
  {
    type: BROWER_LIST.FIREFOX, // firefox扩展程序
    icon: firefoxIcon,
    title: 'firefox',
    isInstall: false,
    installVersion: '',
    description: 'firefoxDescription',
    isNewest: true,
    loading: false, // 是否正在安装
  },
  {
    type: BROWER_LIST['360SE'], // 360扩展程序
    icon: safe360Icon,
    title: '360',
    isInstall: false,
    installVersion: '',
    description: '360Description',
    isNewest: true,
    loading: false, // 是否正在安装
  },
  {
    type: BROWER_LIST['360X'], // 360x扩展程序
    icon: x360Icon,
    title: '360x',
    isInstall: false,
    installVersion: '',
    description: '360xDescription',
    isNewest: true,
    loading: false, // 是否正在安装
  },
]
