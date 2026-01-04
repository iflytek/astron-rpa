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
    versionInfoList: Array<{
      version: number // 版本号
      createTime: string // 创建时间
      updateLog: string // 更新日志
    }>
  }

  interface ComponentManageItem {
    componentId: string
    icon: string
    name: string
    introduction: string
    version: number
    blocked: number // 是否安装: 1 是 0 否 （渲染“移除” 和 “安装” 按钮）
    isLatest: number // 是否是最新版本：1 是 0 否
    latestVersion: number // 最新版本
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
