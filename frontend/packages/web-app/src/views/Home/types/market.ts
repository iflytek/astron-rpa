export enum AppFileStatus {
  normal, // 正常状态
  downloading, // 下载中
  success, // 下载成功
  exception, // 下载失败
  cancled, // 已取消
}

export interface AppFileItem {
  link: string
  appendixId: string
  filename: string
  status: AppFileStatus
  percent?: number
}

export interface cardAppItem {
  appId: string
  appName: string
  appIntro: string
  checkNum: number
  downloadNum: number
  iconUrl: string
  marketId: string
  appVersion: string | number
  securityLevel: string
}
