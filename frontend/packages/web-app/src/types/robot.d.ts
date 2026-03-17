declare namespace RPA {
  interface RobotConfigItem {
    listKey: string
    title: string
    formItems: Array<RPA.AtomParam & { robotId: string, processId: string }>
  }

  /**
   * 组件详情
   */
  interface ComponentDetail {
    name: string // 组件名称
    icon: string // 组件图标
    latestVersion: number // 最新版本
    creatorName: string // 创建人
    introduction: string // 最新版本的简介
    comment?: string // 编辑区便捷描述
    versionInfoList: Array<{
      version: number // 版本号
      createTime: string // 创建时间
      updateLog: string // 更新日志
    }>
  }

  interface ComponentManageItem {
    componentId: string // 组件ID
    appId?: string // 应用ID（仅团队市场组件，用于安装和移除操作）
    icon: string
    name: string
    introduction: string
    comment?: string // 编辑区便捷描述
    version: number
    blocked: number // 是否安装: 1 是 0 否 （渲染"移除" 和 "安装" 按钮）
    isLatest: number // 是否是最新版本：1 是 0 否
    latestVersion: number // 最新版本
    marketId?: string // 团队市场ID（仅团队市场组件，存在即表示是团队市场组件）
    allowOperate?: number // 是否允许操作（例如下架，根据用户角色判断） 0 不允许 ； 1 允许
    dataSource?: 'market' | 'create' // 数据来源：market-团队市场，create-自建组件
  }

  interface AppInfoVo {
    appName: string // 应用名称
    downloadNum: number // 下载量
    checkNum: number // 查看次数
    appIntro: string // 应用介绍
    allowOperate: number // 是否允许操作（例如下架，根据用户角色判断） 0 不允许 ； 1 允许
    obtainStatus: number // 是否可获取（安装）  0: 获取 1: 重新获取（注：组件资源不存在重新获取）
    updateStatus: number // 是否可提示更新 0: 不提示更新 1: 提示更新
    appId: string // 应用id
    marketId: string // 市场id
    marketName: string // 市场名称
    iconUrl: string // 应用图标
    securityLevel: string // 密级标识
    expiryDate: string // 红色密级标识的截止时间
    expiryDateStr: string // 红色密级标识的截止时间提示
    editFlag: boolean // 编辑标志字段
    appVersion: number // 应用版本
    resourceId: string // 组件id
    resourceVersion: number // 资源当前版本号："V" + Integer version
    resourceLatestVersion: number // 资源最新版本号： "V" + Integer latestVersion
    resourceIsLatest: number // 资源最近最新版本， 1 是，0 否
  }

  interface IPage<T> {
    records: T[]
    total: number
    size: number
    current: number
    pages: number
  }

  /**
   * 数据表格
   */
  interface IDataTableSheets {
    active_sheet: string
    filename: string
    project_id: string
    sheets: IDataTableSheet[]
  }

  interface IDataTableSheet {
    name: string
    max_row: number
    max_column: number
    data: string[][]
  }

  interface IUpdateDataTableCell {
    sheet: string
    row: number
    col: number
    value: number | string | boolean
  }
}
