export interface ShortcutItemMap {
  id: string
  name: string
  value: string
  text: string
  validate?: ''
  active?: false
  showSettingCenter?: true // 是否在设置中心显示
}

export interface ShortcutMap {
  [key: string]: ShortcutItemMap
}
