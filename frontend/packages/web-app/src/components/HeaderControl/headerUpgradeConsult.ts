import type { InjectionKey } from 'vue'

export type OpenHeaderUpgradeConsult = () => void

/** Header 内唯一 Auth.Consult（modalOnly）的打开方法，供积分弹层、用户菜单等触发 */
export const OPEN_HEADER_UPGRADE_CONSULT_KEY: InjectionKey<OpenHeaderUpgradeConsult> = Symbol(
  'openHeaderUpgradeConsult',
)
