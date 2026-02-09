import type { IPluginSubscription } from '@rpa/shared'

/**
 * 超简化注册器
 * 支持直接使用，无需复写方法
 */
export class SimpleRegistry<TItem, TKey = string> {
  protected items = new Map<TKey, TItem>()
  protected subscriptions = new Map<TKey, IPluginSubscription>()

  /**
   * 注册项目
   */
  register(key: TKey, item: TItem, onDispose?: () => void): IPluginSubscription {
    this.items.set(key, item)

    const subscription: IPluginSubscription = {
      dispose: () => {
        this.unregister(key)
        onDispose?.()
      },
    }

    this.subscriptions.set(key, subscription)
    return subscription
  }

  /**
   * 注销项目
   */
  unregister(key: TKey): void {
    this.items.delete(key)
    this.subscriptions.delete(key)
  }

  /**
   * 获取项目
   */
  get(key: TKey): TItem | undefined {
    return this.items.get(key)
  }

  /**
   * 获取所有项目
   */
  getAll(): TItem[] {
    return Array.from(this.items.values())
  }

  /**
   * 获取所有键
   */
  getKeys(): TKey[] {
    return Array.from(this.items.keys())
  }

  /**
   * 检查项目是否存在
   */
  has(key: TKey): boolean {
    return this.items.has(key)
  }

  /**
   * 获取项目数量
   */
  size(): number {
    return this.items.size
  }

  /**
   * 清空所有项目
   */
  clear(): void {
    this.items.clear()
    this.subscriptions.clear()
  }
}

/**
 * 多值注册器
 */
export class MultiValueRegistry<TItem, TKey = string> {
  protected items = new Map<TKey, Set<TItem>>()
  protected subscriptions = new Map<string, IPluginSubscription>()

  /**
   * 注册项目
   */
  register(key: TKey, item: TItem, onDispose?: () => void): IPluginSubscription {
    if (!this.items.has(key)) {
      this.items.set(key, new Set())
    }
    this.items.get(key)!.add(item)

    const subscriptionId = `${String(key)}-${this.generateItemId(item)}`
    const subscription: IPluginSubscription = {
      dispose: () => {
        this.unregister(key, item)
        onDispose?.()
      },
    }

    this.subscriptions.set(subscriptionId, subscription)
    return subscription
  }

  /**
   * 注销项目
   */
  unregister(key: TKey, item: TItem): void {
    const items = this.items.get(key)
    if (items) {
      items.delete(item)
      if (items.size === 0) {
        this.items.delete(key)
      }
    }

    const subscriptionId = `${String(key)}-${this.generateItemId(item)}`
    this.subscriptions.delete(subscriptionId)
  }

  /**
   * 获取项目的所有值
   */
  get(key: TKey): TItem[] {
    return Array.from(this.items.get(key) || [])
  }

  /**
   * 获取所有项目
   */
  getAll(): TItem[] {
    const allItems: TItem[] = []
    this.items.forEach((items) => {
      allItems.push(...items)
    })
    return allItems
  }

  /**
   * 获取所有键
   */
  getKeys(): TKey[] {
    return Array.from(this.items.keys())
  }

  /**
   * 检查项目是否存在
   */
  has(key: TKey, item: TItem): boolean {
    return this.items.get(key)?.has(item) || false
  }

  /**
   * 获取项目数量
   */
  size(): number {
    let count = 0
    this.items.forEach((items) => {
      count += items.size
    })
    return count
  }

  /**
   * 清空所有项目
   */
  clear(): void {
    this.items.clear()
    this.subscriptions.clear()
  }

  /**
   * 生成项目ID
   */
  private generateItemId(_item: TItem): string {
    return Math.random().toString(36).substr(2, 9)
  }
}

/**
 * 事件注册器
 */
export class EventRegistry<TArgs extends any[] = any[]> {
  protected callbacks = new Map<string, Set<(...args: TArgs) => any>>()
  protected subscriptions = new Map<string, IPluginSubscription>()

  /**
   * 注册事件回调
   */
  register(event: string, callback: (...args: TArgs) => any): IPluginSubscription {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, new Set())
    }
    this.callbacks.get(event)!.add(callback)

    const subscriptionId = `${event}-${this.generateCallbackId(callback)}`
    const subscription: IPluginSubscription = {
      dispose: () => {
        this.unregister(event, callback)
      },
    }

    this.subscriptions.set(subscriptionId, subscription)
    return subscription
  }

  /**
   * 注销事件回调
   */
  unregister(event: string, callback: (...args: TArgs) => any): void {
    const callbacks = this.callbacks.get(event)
    if (callbacks) {
      callbacks.delete(callback)
      if (callbacks.size === 0) {
        this.callbacks.delete(event)
      }
    }

    const subscriptionId = `${event}-${this.generateCallbackId(callback)}`
    this.subscriptions.delete(subscriptionId)
  }

  /**
   * 触发事件
   */
  async trigger(event: string, ...args: TArgs): Promise<void> {
    const callbacks = this.callbacks.get(event)
    if (callbacks && callbacks.size > 0) {
      const promises = Array.from(callbacks).map((callback) => {
        try {
          return Promise.resolve(callback(...args))
        }
        catch (error) {
          console.error(`[EventRegistry] Error in callback for event ${event}:`, error)
          return Promise.resolve()
        }
      })

      await Promise.all(promises)
    }
  }

  /**
   * 获取所有事件
   */
  getEvents(): string[] {
    return Array.from(this.callbacks.keys())
  }

  /**
   * 获取事件的回调数量
   */
  getCallbackCount(event: string): number {
    return this.callbacks.get(event)?.size || 0
  }

  /**
   * 清空所有回调
   */
  clear(): void {
    this.callbacks.clear()
    this.subscriptions.clear()
  }

  /**
   * 生成回调ID
   */
  private generateCallbackId(callback: (...args: TArgs) => any): string {
    return callback.name || 'anonymous'
  }
}
