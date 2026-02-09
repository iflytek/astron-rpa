import type { IPluginSettings, IPluginSubscription, ISettingsTabContribution } from '@rpa/shared'

import { SimpleRegistry } from './_registry'

/**
 * 设置页面Tab扩展点 - 直接使用基础类，无需复写
 */
export const settingsExtension = new SimpleRegistry<ISettingsTabContribution, string>()

/**
 * 设置注册器实现
 */
export class PluginSettings implements IPluginSettings {
  constructor() {}

  registerSettingsTab(tab: ISettingsTabContribution): IPluginSubscription {
    return settingsExtension.register(tab.id, tab)
  }

  unregisterSettingsTab(id: string): void {
    settingsExtension.unregister(id)
  }

  getSettingsTabs(): ISettingsTabContribution[] {
    return settingsExtension.getAll()
  }
}
