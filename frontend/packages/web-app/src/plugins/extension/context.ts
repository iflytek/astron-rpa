import type {
  IPluginContext,
  IPluginExtension,
  IPluginSubscription,
} from '@rpa/shared'

import { PluginSettings, settingsExtension } from './extensions/settings'

/**
 * 插件扩展实现
 */
export class PluginExtension implements IPluginExtension {
  constructor(
    public id: string,
    public extensionPath: string,
    public isActive: boolean,
    public packageJSON: any,
  ) {}
}

/**
 * 插件订阅实现
 */
export class PluginSubscription implements IPluginSubscription {
  private disposed = false

  constructor(private disposeFn: () => void) {}

  dispose(): void {
    if (!this.disposed) {
      this.disposeFn()
      this.disposed = true
    }
  }
}

/**
 * 插件上下文管理器
 */
export class PluginContextManager {
  private static instance: PluginContextManager

  private constructor() {}

  /**
   * 获取单例实例
   */
  static getInstance(): PluginContextManager {
    if (!this.instance) {
      this.instance = new PluginContextManager()
    }
    return this.instance
  }

  /**
   * 创建插件上下文
   */
  createContext(extension: IPluginExtension): IPluginContext {
    const subscriptions: IPluginSubscription[] = []

    return {
      extension,
      subscriptions,
      settings: new PluginSettings(),
    }
  }

  /**
   * 获取扩展点实例（用于系统级操作）
   */
  getExtensions() {
    return {
      settings: settingsExtension,
    }
  }

  /**
   * 清空所有扩展点
   */
  clearAll(): void {
    settingsExtension.clear()
  }

  /**
   * 获取扩展点统计信息
   */
  getStats() {
    return {
      settingsTabs: settingsExtension.size(),
    }
  }
}

/**
 * 便捷的工厂函数
 */
export function createPluginContext(extension: IPluginExtension): IPluginContext {
  return PluginContextManager.getInstance().createContext(extension)
}

/**
 * 获取插件上下文管理器实例
 */
export function getPluginContextManager(): PluginContextManager {
  return PluginContextManager.getInstance()
}
