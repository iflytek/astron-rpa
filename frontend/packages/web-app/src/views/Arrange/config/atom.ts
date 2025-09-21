import { ATOM_FORM_TYPE } from '@/constants/atom'

export type ATOMTABKEYS = 'BASE_ATOM' | 'EXT_ATOM'

export interface ATOMTABDATA {
  title: string
  value: ATOMTABKEYS
}

export const ATOMTABS: Array<ATOMTABDATA> = [
  {
    title: 'atomicPower',
    value: 'BASE_ATOM',
  },
  {
    title: 'extensionComponents',
    value: 'EXT_ATOM',
  },
]

// 流程变量类型
export const GLOBAL_VAR_TYPE = 'globalVariables' // 全局变量
export const PROCESS_VAR_TYPE = 'processVariables' // 局部变量
export const PARAMETER_VAR_TYPE = 'configParameters' // 配置参数

export const PICK_TYPE_CV = 'CV' // 拾取类型CV

// 原子项的input只能输入数值类型
export const INPUT_NUMBER_TYPE_ARR = ['Float', 'Int']

// 只能输入一个变量的类型 浏览器对象，excel对象， word对象
export const SINGLE_VAR_TYPE_ARR = ['browser_obj', 'excel', 'doc']

// 创建dom元素的来源 origin
export const ORIGIN_BUTTON = 'button' // 按钮
export const ORIGIN_VAR = 'var_input' // 变量输入框
export const ORIGIN_SPECIAL = 'special' // 特殊混合输入框

// 原子能力基础信息表单配置
export const BASE_FORM = [
  {
    formType: {
      type: 'INPUT',
      params: {
        values: [],
      },
    },
    title: '任务名称',
    key: 'baseName',
    noInput: true,
    value: '',
  },
  {
    formType: {
      type: 'INPUT',
      params: {
        values: ['string'],
      },
    },
    title: '任务别名',
    key: 'anotherName',
    value: '',
  },
]

// 默认颜色列表
export const DEFAULT_COLOR_LIST = [
  '#ff7e79',
  '#fefe7f',
  '#00ff81',
  '#007ffe',
  '#ff80c0',
  '#ff0104',
  '#00fcff',
  '#847cc2',
  '#fe00fe',
  '#7e0101',
  '#fc7f01',
  '#027e04',
  '#65b2f3',
  '#f9b714',
  '#068081',
  '#8305a1',
  '#b0cf29',
  '#0bfa49',
  '#9e255e',
  '#ffffff',
]

// cv拾取匹配度
export const MATCH_DEGREE = {
  0: '模糊',
  95: '默认',
  100: '精准',
}

export const SELECT_VALUE_TYPES = [
  ATOM_FORM_TYPE.RADIO,
  ATOM_FORM_TYPE.CHECKBOX,
  ATOM_FORM_TYPE.CHECKBOXGROUP,
  ATOM_FORM_TYPE.SWITCH,
  ATOM_FORM_TYPE.SELECT,
  ATOM_FORM_TYPE.FONTSIZENUMBER,
  ATOM_FORM_TYPE.DEFAULTDATEPICKER,
  ATOM_FORM_TYPE.RANGEDATEPICKER,
]

export const CATEGORY_MAP = {
  process: '子流程',
  module: '子模块',
}
