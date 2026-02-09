import type { IPluginContext } from '@rpa/shared'
import { definePlugin } from '@rpa/shared'
import { markRaw } from 'vue'

import Content from './Content.vue'

export default definePlugin({
  activate: async (_context: IPluginContext) => {
    console.log('[SimplePluginExample] 插件激活中...')
  },
  deactivate: () => {
    console.log('[SimplePluginExample] 插件停用中...')
    console.log('[SimplePluginExample] 插件停用完成')
  },
  contributes: {
    settingsTabs: [
      {
        id: 'text',
        title: '测试',
        icon: 'plugin',
        content: markRaw(Content),
      },
    ],
  },
})
