import type { ComponentResolver } from 'unplugin-vue-components/types'

/**
 * 自定义组件解析器，用于替换 a-modal 为 GlobalModal
 */
export function ModalReplacementResolver(): ComponentResolver {
  return {
    type: 'component',
    resolve: (name: string) => {
      // 当遇到 AModal 或 a-modal 时，返回 GlobalModal 的导入信息
      if (name === 'AModal') {
        return {
          name: 'default',
          from: '@/components/GlobalModal/index.vue',
        }
      }
    },
  }
}
