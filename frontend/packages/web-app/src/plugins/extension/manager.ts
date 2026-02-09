import { createInstance } from '@module-federation/enhanced/runtime'
import type { ModuleFederation } from '@module-federation/enhanced/runtime'
import type {
  IPluginConfig,
  IPluginContext,
  IPluginContributes,
  IPluginModule,
} from '@rpa/shared'
import to from 'await-to-js'
import { EventEmitter } from 'eventemitter3'
import * as Pinia from 'pinia'
import * as Vue from 'vue'

import { utilsManager } from '@/platform'

import { createPluginContext, getPluginContextManager, PluginExtension } from './context'

/**
 * 插件实例接口
 */
export interface IPluginInstance {
  /** 插件配置 */
  config: IPluginConfig
  /** 插件模块 */
  module?: IPluginModule
  /** 插件状态 */
  status: 'unloaded' | 'loading' | 'loaded' | 'failed'
  /** 插件错误信息 */
  error?: string
  /** 插件实例ID */
  instanceId: string
  /** 插件是否已激活 */
  isActivated: boolean
}

/**
 * 插件管理器配置
 */
export interface IPluginManagerConfig {
  /** 插件API基础URL */
  apiBaseUrl: string
  /** 插件缓存时间（毫秒） */
  cacheTime?: number
  /** 最大并发加载数 */
  maxConcurrentLoads?: number
  /** 是否启用插件缓存 */
  enableCache?: boolean
  /** 插件超时时间（毫秒） */
  timeout?: number
}

/**
 * 插件管理器事件
 */
export interface IPluginManagerEvents {
  /** 插件安装事件 */
  'plugin:install': (instance: IPluginInstance) => void
  /** 插件卸载事件 */
  'plugin:uninstall': (instance: IPluginInstance) => void
  /** 插件激活事件 */
  'plugin:activate': (instance: IPluginInstance) => void
  /** 插件停用事件 */
  'plugin:deactivate': (instance: IPluginInstance) => void
  /** 插件加载事件 */
  'plugin:load': (instance: IPluginInstance) => void
  /** 插件错误事件 */
  'plugin:error': (instance: IPluginInstance, error: Error) => void
}

/**
 * 插件管理器
 */
export class PluginManager extends EventEmitter<IPluginManagerEvents> {
  private plugins = new Map<string, IPluginInstance>()
  private config: Required<IPluginManagerConfig>
  private loadingQueue: Set<string> = new Set()
  private cache = new Map<string, { data: IPluginConfig[], timestamp: number }>()
  private mf: ModuleFederation

  constructor(config: IPluginManagerConfig) {
    super()

    this.config = {
      apiBaseUrl: config.apiBaseUrl,
      cacheTime: config.cacheTime ?? 5 * 60 * 1000, // 5分钟
      maxConcurrentLoads: config.maxConcurrentLoads ?? 3,
      timeout: config.timeout ?? 30000, // 30秒
      enableCache: config.enableCache ?? true,
    }

    this.mf = createInstance({
      name: 'host',
      remotes: [],
      shared: {
        vue: {
          version: __VUE_VERSION__,
          scope: 'default',
          lib: () => Vue,
          shareConfig: {
            singleton: true,
            requiredVersion: '^3.5.0',
          },
        },
        pinia: {
          version: __PINIA_VERSION__,
          scope: 'default',
          lib: () => Pinia,
          shareConfig: {
            singleton: true,
            requiredVersion: '^3.0.0',
          },
        },
      },
    })
  }

  /**
   * 获取插件列表
   */
  async getPluginList(): Promise<IPluginConfig[]> {
    const cacheKey = 'plugin-list'

    // 检查缓存
    if (this.config.enableCache) {
      const cached = this.cache.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < this.config.cacheTime) {
        return cached.data
      }
    }

    try {
      const [error, plugins] = await to(utilsManager.getPluginList())

      if (error) {
        throw new Error(`Failed to fetch plugins: ${error.message}`)
      }

      // 缓存结果
      if (this.config.enableCache) {
        this.cache.set(cacheKey, {
          data: plugins,
          timestamp: Date.now(),
        })
      }

      return plugins
    }
    catch (error) {
      console.error('Failed to fetch plugin list:', error)
      throw error
    }
  }

  /**
   * 安装插件
   */
  async installPlugin(config: IPluginConfig): Promise<IPluginInstance> {
    const instanceId = `${config.name}@${config.version}`

    // 检查是否已安装
    if (this.plugins.has(instanceId)) {
      return this.plugins.get(instanceId)!
    }

    const instance: IPluginInstance = {
      config,
      status: 'unloaded',
      instanceId,
      isActivated: false,
    }

    this.plugins.set(instanceId, instance)
    this.emit('plugin:install', instance)

    return instance
  }

  /**
   * 卸载插件
   */
  async uninstallPlugin(instanceId: string): Promise<void> {
    const instance = this.plugins.get(instanceId)
    if (!instance) {
      throw new Error(`Plugin ${instanceId} not found`)
    }

    // 如果插件已激活，先停用
    if (instance.isActivated) {
      await this.deactivatePlugin(instanceId)
    }

    this.plugins.delete(instanceId)
    this.emit('plugin:uninstall', instance)
  }

  /**
   * 加载插件
   */
  async loadPlugin(instanceId: string): Promise<IPluginInstance> {
    const instance = this.plugins.get(instanceId)
    if (!instance) {
      throw new Error(`Plugin ${instanceId} not found`)
    }

    if (instance.status === 'loaded') {
      return instance
    }

    if (instance.status === 'loading') {
      // 等待加载完成
      return new Promise((resolve, reject) => {
        const checkStatus = () => {
          const currentInstance = this.plugins.get(instanceId)
          if (!currentInstance) {
            reject(new Error(`Plugin ${instanceId} not found`))
            return
          }

          if (currentInstance.status === 'loaded') {
            resolve(currentInstance)
          }
          else if (currentInstance.status === 'failed') {
            reject(new Error(currentInstance.error || 'Plugin loading failed'))
          }
          else {
            setTimeout(checkStatus, 100)
          }
        }
        checkStatus()
      })
    }

    // 检查并发加载限制
    if (this.loadingQueue.size >= this.config.maxConcurrentLoads) {
      throw new Error('Maximum concurrent plugin loads reached')
    }

    this.loadingQueue.add(instanceId)
    instance.status = 'loading'

    try {
      // 设置远程配置
      this.mf.registerRemotes([{
        name: instance.config.name,
        entry: instance.config.entry,
      }])

      // 获取远程模块
      const remoteModule = await Promise.race([
        this.mf.loadRemote(`${instance.config.name}/index`).then((res: any) => res.default),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Plugin loading timeout')), this.config.timeout),
        ),
      ]) as any

      instance.module = remoteModule
      instance.status = 'loaded'
      instance.error = undefined

      this.emit('plugin:load', instance)

      return instance
    }
    catch (error) {
      instance.status = 'failed'
      instance.error = error instanceof Error ? error.message : String(error)
      this.emit('plugin:error', instance, error instanceof Error ? error : new Error(String(error)))
      throw error
    }
    finally {
      this.loadingQueue.delete(instanceId)
    }
  }

  /**
   * 激活插件
   */
  async activatePlugin(instanceId: string): Promise<void> {
    const instance = this.plugins.get(instanceId)
    if (!instance) {
      throw new Error(`Plugin ${instanceId} not found`)
    }

    if (instance.isActivated) {
      console.log(`[PluginManager] Plugin ${instance.config.name} is already activated`)
      return
    }

    if (!instance.module) {
      throw new Error(`Plugin ${instance.config.name} module not loaded`)
    }

    try {
      console.log(`[PluginManager] Activating plugin ${instance.config.name}`)

      // 创建插件上下文
      const extension = new PluginExtension(
        instance.config.name,
        instance.config.entry,
        false,
        instance.config,
      )

      const context = createPluginContext(extension)

      // 执行插件激活函数
      if (instance.module.activate) {
        await instance.module.activate(context)
      }

      // 注册插件贡献点
      if (instance.module.contributes) {
        this.registerContributions(instance.config.name, instance.module.contributes, context)
      }

      // 标记为已激活
      instance.isActivated = true
      this.emit('plugin:activate', instance)

      console.log(`[PluginManager] Plugin ${instance.config.name} activated successfully`)
    }
    catch (error) {
      console.error(`[PluginManager] Failed to activate plugin ${instance.config.name}:`, error)
      throw error
    }
  }

  /**
   * 停用插件
   */
  async deactivatePlugin(instanceId: string): Promise<void> {
    const instance = this.plugins.get(instanceId)
    if (!instance) {
      throw new Error(`Plugin ${instanceId} not found`)
    }

    if (!instance.isActivated) {
      console.log(`[PluginManager] Plugin ${instance.config.name} is not activated`)
      return
    }

    try {
      console.log(`[PluginManager] Deactivating plugin ${instance.config.name}`)

      // 执行插件停用函数
      if (instance.module?.deactivate) {
        await instance.module.deactivate()
      }

      // 注销插件贡献点
      if (instance.module?.contributes) {
        this.unregisterContributions(instance.config.name, instance.module.contributes)
      }

      // 标记为未激活
      instance.isActivated = false
      this.emit('plugin:deactivate', instance)

      console.log(`[PluginManager] Plugin ${instance.config.name} deactivated successfully`)
    }
    catch (error) {
      console.error(`[PluginManager] Failed to deactivate plugin ${instance.config.name}:`, error)
      throw error
    }
  }

  /**
   * 注册插件贡献点
   */
  private registerContributions(_pluginId: string, contributes: IPluginContributes, context: IPluginContext): void {
    // const extensions = PluginContextFactory.getExtensions()

    // 注册设置Tab
    if (contributes.settingsTabs) {
      contributes.settingsTabs.forEach((tab) => {
        context.settings.registerSettingsTab(tab)
      })
    }
  }

  /**
   * 注销插件贡献点
   */
  private unregisterContributions(pluginId: string, _contributes: any): void {
    // 这里可以实现注销逻辑
    console.log(`[PluginManager] Unregistering contributions for plugin: ${pluginId}`)
  }

  /**
   * 批量安装插件
   */
  async installPlugins(configs: IPluginConfig[]): Promise<IPluginInstance[]> {
    const instances: IPluginInstance[] = []

    for (const config of configs) {
      try {
        const instance = await this.installPlugin(config)
        instances.push(instance)
      }
      catch (error) {
        console.error(`Failed to install plugin ${config.name}:`, error)
      }
    }

    return instances
  }

  /**
   * 批量加载插件
   */
  async loadPlugins(instanceIds: string[]): Promise<IPluginInstance[]> {
    const loadPromises = instanceIds.map(id => this.loadPlugin(id))
    return Promise.allSettled(loadPromises).then(results =>
      results
        .filter((result): result is PromiseFulfilledResult<IPluginInstance> => result.status === 'fulfilled')
        .map(result => result.value),
    )
  }

  /**
   * 获取插件实例
   */
  getPlugin(instanceId: string): IPluginInstance | undefined {
    return this.plugins.get(instanceId)
  }

  /**
   * 获取所有插件实例
   */
  getAllPlugins(): IPluginInstance[] {
    return Array.from(this.plugins.values())
  }

  /**
   * 获取已加载的插件
   */
  getLoadedPlugins(): IPluginInstance[] {
    return this.getAllPlugins().filter(plugin => plugin.status === 'loaded')
  }

  /**
   * 检查插件是否已安装
   */
  isPluginInstalled(instanceId: string): boolean {
    return this.plugins.has(instanceId)
  }

  /**
   * 检查插件是否已加载
   */
  isPluginLoaded(instanceId: string): boolean {
    const instance = this.plugins.get(instanceId)
    return instance?.status === 'loaded'
  }

  /**
   * 清除缓存
   */
  clearCache(): void {
    this.cache.clear()
  }

  /**
   * 获取扩展点实例
   */
  getExtensions() {
    return getPluginContextManager().getExtensions()
  }

  /**
   * 销毁插件管理器
   */
  async destroy(): Promise<void> {
    // 停用所有插件
    const instances = this.getAllPlugins()
    for (const instance of instances) {
      try {
        await this.deactivatePlugin(instance.instanceId)
        await this.uninstallPlugin(instance.instanceId)
      }
      catch (error) {
        console.error(`Failed to destroy plugin ${instance.instanceId}:`, error)
      }
    }

    this.plugins.clear()
    this.loadingQueue.clear()
    this.cache.clear()
    this.removeAllListeners()
  }
}
