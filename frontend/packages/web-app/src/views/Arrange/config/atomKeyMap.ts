export const If = 'Code.If'
export const IfEnd = 'Code.IfEnd'
export const ElseIf = 'Code.ElseIf'
export const ElseIfEnd = 'Code.ElseIfEnd'
export const Else = 'Code.Else'
export const ElseEnd = 'Code.ElseEnd'
export const Try = 'Code.Try'
export const TryEnd = 'Code.TryEnd'
export const Catch = 'Code.Catch'
export const CatchEnd = 'Code.CatchEnd'
export const Finally = 'Code.Finally'
export const FinallyEnd = 'Code.FinallyEnd'
export const ForStep = 'Code.ForStep'
export const ForStepEnd = 'Code.ForStepEnd'
export const ForDict = 'Code.ForDict'
export const ForDictEnd = 'Code.ForDictEnd'
export const ForList = 'Code.ForList'
export const ForExcelContent = 'Excel.loop_excel_content'
export const ForBrowserSimilar = 'BrowserElement.loop_similar'
export const ForDataTableLoop = 'DataTable.loop_data_table'
export const ForListEnd = 'Code.ForListEnd'
export const While = 'Code.While'
export const WhileEnd = 'Code.WhileEnd'
export const ForEnd = 'Code.ForEnd'
// const Netbreak = 'Code.Netbreak'  // 网络断联检测 TODO
// const NetbreakEnd =  'Code.NetbreakEnd'
export const Break = 'Code.Break'
export const Continue = 'Code.Continue'
export const Group = 'Code.Group'
export const GroupEnd = 'Code.GroupEnd'
export const CvImageExist = 'CV.is_image_exist' // 判断图像存在
export const CvImageExistEnd = 'CV.is_image_exist_end' // 判断图像存在结束
export const FileExist = 'File.file_exist'
export const FolderExist = 'Folder.folder_exist'
export const WindowExist = 'Window.exist'
export const Process = 'Code.Process' // 运行子流程
export const Module = 'Script.module' // 运行子模块

export const IF_TEXT = 'if'
export const ELSE_IF_TEXT = 'elseif'
export const ELSE_TEXT = 'else'
export const IF_END_TEXT = 'ifend'
export const WHILE_TEXT = 'while'
export const FOR_STEP_TEXT = 'stepfor'
export const FOR_DICT_TEXT = 'dictfor'
export const FOR_LIST_TEXT = 'listfor'
export const FOR_EXCEL_CONTENT = 'excelcontentfor'
export const FOR_BRO_SIMILAR = 'borsimilarfor'
export const FOR_DATA_TABLE_LOOP = 'datatablefor'
export const FOR_END_TEXT = 'forend'
export const TRY_TEXT = 'try'
export const CATCH_TEXT = 'catch'
export const FINALLY_TEXT = 'finally'
export const TRY_END_TEXT = 'tryend'
export const GROUP_TEXT = 'group'
export const GROUP_END_TEXT = 'groupend'

// 嵌套类节点key对应的结束节点key
export const LOOP_END_MAP = {
  [If]: IfEnd,
  [Try]: Catch,
  [Catch]: TryEnd,
  // [Finally]: TryEnd,
  [ForStep]: ForEnd,
  [ForDict]: ForEnd,
  [ForList]: ForEnd,
  [ForExcelContent]: ForEnd,
  [ForBrowserSimilar]: ForEnd,
  [ForDataTableLoop]: ForEnd,
  [While]: ForEnd,
  [Group]: GroupEnd,
  // [Netbreak]: NetbreakEnd,  // 网络断联检测 TODO
  [CvImageExist]: IfEnd,
  [FileExist]: IfEnd,
  [FolderExist]: IfEnd,
  [WindowExist]: IfEnd,
}

// 结束节点key对应的嵌套类节点key
export const LOOP_START_MAP = {
  [IfEnd]: If,
  [TryEnd]: Try,
  [WhileEnd]: While,
  [GroupEnd]: Group,
  // [NetbreakEnd]: Netbreak,  // 网络断联检测 TODO
  [CvImageExistEnd]: CvImageExist,
}

// 配置结束节点之后下一个节点的类型
export const hideEndNextMap = {
  [IfEnd]: [ElseIf, Else],
  [ElseIfEnd]: [ElseIf, Else],
  [TryEnd]: [Catch, Finally],
  [CatchEnd]: [Finally],
}

export const LOOP_END = [
  IfEnd,
  ElseIfEnd,
  ElseEnd,
  TryEnd,
  CatchEnd,
  FinallyEnd,
  ForStepEnd,
  ForListEnd,
  ForDictEnd,
  ForEnd,
  WhileEnd,
  GroupEnd,
  CvImageExistEnd,
]

export const CONVERT_MAP = {
  [If]: IF_TEXT,
  [ElseIf]: ELSE_IF_TEXT,
  [Else]: ELSE_TEXT,
  [IfEnd]: IF_END_TEXT,
  [Try]: TRY_TEXT,
  [Catch]: CATCH_TEXT,
  [Finally]: FINALLY_TEXT,
  [TryEnd]: TRY_END_TEXT,
  [ForStep]: FOR_STEP_TEXT,
  [ForDict]: FOR_DICT_TEXT,
  [ForList]: FOR_LIST_TEXT,
  [ForExcelContent]: FOR_EXCEL_CONTENT,
  [ForBrowserSimilar]: FOR_BRO_SIMILAR,
  [ForDataTableLoop]: FOR_DATA_TABLE_LOOP,
  [ForEnd]: FOR_END_TEXT,
  [While]: WHILE_TEXT,
  [Group]: GROUP_TEXT,
  [GroupEnd]: GROUP_END_TEXT,
  [CvImageExist]: IF_TEXT,
  [FileExist]: IF_TEXT,
  [FolderExist]: IF_TEXT,
  [WindowExist]: IF_TEXT,
}

export const IS_SAME_GROUP = [GROUP_TEXT, IF_TEXT, ELSE_IF_TEXT, ELSE_TEXT, TRY_TEXT, CATCH_TEXT, FINALLY_TEXT, FOR_STEP_TEXT, FOR_DICT_TEXT, FOR_LIST_TEXT, WHILE_TEXT]

export const hideEndKeys = Object.keys(hideEndNextMap)

/**
 * 配置前置和后置节点的类型
 * ELSE的前置节点必须是IF, ELSEIF
 * ELSEIF的前置节点必须是IF, ELSEIF
 * TRY的后置节点必须是CATCH, FINALLY
 * CATCH的前置节点必须是TRY
 * FINALLY的前置节点必须是TRY, CATCH
 */
export const orderMap = {
  [Else]: {
    pre: [If, ElseIf],
    preDesc: '“else”组件前同级组件必须是“if条件”组件或者“esle if”组件',
  },
  [ElseIf]: {
    pre: [If, ElseIf],
    preDesc: '“else if”组件前同级组件必须是“if条件”组件或者“esle if”组件',
  },
  [Try]: {
    next: [Catch, Finally],
    nextDesc: '“try”组件后同级组件必须是“catch”组件或者“finally”组件',
  },
  [Catch]: {
    pre: [Try],
    preDesc: '“catch”组件前同级组件必须是“try”组件',
  },
  [Finally]: {
    pre: [Try, Catch],
    preDesc: '“finally”组件前同级组件必须是“try”组件或者“catch”组件',
  },
}
