// 原子能力相关的常量

// 原子项类型
export enum ATOM_FORM_TYPE {
  INPUT = 'INPUT', // input类型
  SELECT = 'SELECT', // select类型
  CHECKBOX = 'CHECKBOX', // checkbox类型
  CHECKBOXGROUP = 'CHECKBOXGROUP', // checkboxgroup类型
  RADIO = 'RADIO', // radio类型
  SWITCH = 'SWITCH', // switch类型
  PYTHON = 'PYTHON', // python类型
  VARIABLE = 'VARIABLE', // var类型
  FILE = 'FILE', // file类型
  TEXTAREAMODAL = 'TEXTAREAMODAL', // 文本弹窗类型
  ELEMENT = 'ELEMENT', // element类型
  DATETIME = 'DATETIME', // datetime类型
  COLOR = 'COLOR', // color类型
  PICK = 'PICK', // pick类型
  RESULT = 'RESULT', // result类型
  KEYBOARD = 'KEYBOARD', // keyboard类型
  FONTSIZENUMBER = 'FONTSIZENUMBER', // 字号数字类型
  MODALBUTTON = 'MODALBUTTON', // 弹窗按钮类型
  DEFAULTDATEPICKER = 'DEFAULTDATEPICKER', // 默认日期选择器
  RANGEDATEPICKER = 'RANGEDATEPICKER', // 范围日期选择器
  OPTIONSLIST = 'OPTIONSLIST', // 选项列表
  CV_IMAGE = 'CVIMAGE', // cv图片类型
  CVPICK = 'CVPICK', // cvpick 类型
  GRID = 'GRID', // 九宫格 类型
  SLIDER = 'SLIDER', // 九宫格 类型
  DEFAULTPASSWORD = 'DEFAULTPASSWORD', // 普通密码类型
  PROCESS_PARAM = 'PROCESSPARAM', // 配置参数
  FACTORELEMENT = 'FACTORELEMENT', // 合同要素
  CONTENTPASTE = 'CONTENTPASTE', // 内容粘贴
  MOUSEPOSITION = 'MOUSEPOSITION', // 鼠标位置拾取
  SCRIPTPARAMS = 'SCRIPTPARAMS', // 脚本参数管理
  REMOTEPARAMS = 'REMOTEPARAMS', // 远程参数
  REMOTEFOLDERS = 'REMOTEFOLDERS', // 远程文件夹选择
}

// 保存到py端的类型
export const OTHER_IN_TYPE = 'other' // other类型
export const PY_IN_TYPE = 'python' // python类型
export const VAR_IN_TYPE = 'var' // var类型
export const GLOBAL_VAR_IN_TYPE = 'g_var' // 全局变量类型
export const PARAMETER_VAR_IN_TYPE = 'p_var' // 配置参数类型
export const ELEMENT_IN_TYPE = 'element' // element类型
export const CV_IN_TYPE = 'cv' // element类型
export const PROCESS_IN_TYPE = 'process' // process类型

// 原子能力输入输出变量类型
export enum VARIABLE_TYPE {
  BROWSER = 'Browser',
  EXCEL = 'ExcelObj',
  WORD = 'DocxObj',
}

// 变量选择器中需要限制选择的变量类型
export const LIMIT_VARIABLE_SELECT = [VARIABLE_TYPE.BROWSER, VARIABLE_TYPE.EXCEL, VARIABLE_TYPE.WORD]
