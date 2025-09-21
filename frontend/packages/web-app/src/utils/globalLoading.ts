/** @format */

import BUS from '@/utils/eventBus'

const $loading = {
  /**
   * @param options.msg loading 提示信息
   * @param options.timeout  显示时间 单位秒
   * @param options.exit 是否退出按钮
   * @param options.exitCallback 退出按钮回调
   */
  open: (options: { msg?: string, timeout?: number, exit?: boolean, exitCallback?: () => void }) => {
    const { msg = '', timeout = 200, exit = false, exitCallback } = options
    BUS.$emit('isLoading', { isLoading: true, text: msg, timeout, exit, exitCallback })
  },
  /**
   * @param immediate 是否立即关闭
   */
  close: (immediate?: boolean) => {
    BUS.$emit('isLoading', { isLoading: false, immediate })
  },
}
export default $loading
