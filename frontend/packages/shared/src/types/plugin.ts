import type { Component } from 'vue'

/**
 * 插件配置接口
 */
export interface IPluginConfig {
  /** 插件名称 */
  name: string
  /** 插件版本 */
  version: string
  /** 插件描述 */
  description?: string
  /** 插件入口URL */
  entry: string
  /** 插件是否启用 */
  enabled?: boolean
  /** 插件贡献点 */
  contributes?: IPluginContributes
}

/**
 * 插件模块接口
 */
export interface IPluginModule {
  /** 插件激活函数 */
  activate?: (context: IPluginContext) => Promise<void> | void
  /** 插件停用函数 */
  deactivate?: () => Promise<void> | void
  /** 插件贡献点 */
  contributes?: IPluginContributes
}

/**
 * 插件贡献点接口
 */
export interface IPluginContributes {
  /** 设置页面贡献 */
  settingsTabs?: ISettingsTabContribution[]
}

/**
 * 设置页面Tab贡献接口
 */
export interface ISettingsTabContribution {
  /** Tab ID */
  id: string
  /** Tab标题 */
  title: string
  /** Tab图标 */
  icon: string
  /** Tab顺序 */
  order?: number
  /** Tab渲染内容 */
  content: Component
}

/**
 * 插件上下文接口
 */
export interface IPluginContext {
  /** 插件扩展信息 */
  extension: IPluginExtension
  /** 订阅集合 */
  subscriptions: IPluginSubscription[]
  /** 设置注册器 */
  settings: IPluginSettings
}

/**
 * 插件扩展接口
 */
export interface IPluginExtension {
  /** 扩展ID */
  id: string
  /** 扩展路径 */
  extensionPath: string
  /** 扩展是否激活 */
  isActive: boolean
  /** 扩展包JSON */
  packageJSON: any
}

/**
 * 插件订阅接口
 */
export interface IPluginSubscription {
  /** 取消订阅 */
  dispose: () => void
}

/**
 * 设置注册器接口
 */
export interface IPluginSettings {
  /** 注册设置Tab */
  registerSettingsTab: (tab: ISettingsTabContribution) => IPluginSubscription
  /** 注销设置Tab */
  unregisterSettingsTab: (id: string) => void
  /** 获取所有设置Tab */
  getSettingsTabs: () => ISettingsTabContribution[]
}
