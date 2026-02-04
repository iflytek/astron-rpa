import { ATOM_FORM_TYPE } from '@/constants/atom'

/**
 * 创建表单示例的辅助函数
 * 
 * 基础字段说明（所有类型通用）：
 * - formType: { type: string, params?: object } - 必填，表单类型配置
 * - key: string - 必填，表单唯一标识
 * - title: string - 必填，表单标题
 * - value: 根据类型不同 - 必填，表单值
 * - types: string - 非必填，变量类型（如 'Any', 'Str', 'Int' 等）
 * - tip: string - 非必填，提示信息
 * - required: boolean - 非必填，是否必填
 * - options: Array<{ label: string, value: any }> - 非必填，选项列表（用于 CHECKBOXGROUP, RADIO, SELECT, SWITCH）
 * - min: number - 非必填，最小值（用于 FONTSIZENUMBER）
 * - max: number - 非必填，最大值（用于 FONTSIZENUMBER）
 * - step: number - 非必填，步长（用于 FONTSIZENUMBER，默认 1）
 */
function createFormItemExample(item: { type: string }, index: number): RPA.AtomDisplayItem {
  const baseItem: RPA.AtomDisplayItem = {
    types: 'Any',
    key: `demo_${item.type.toLowerCase()}_${index}`,
    title: `${item.type} 示例`,
    tip: `这是 ${item.type} 类型的表单示例`,
    value: [],
  }

  switch (item.type) {
    // ========== editItem 类型（除了 ATOM_FORM_TYPE.FILE, 其他都需要包含 ATOM_FORM_TYPE.INPUT 才能使用） ==========
    
    /**
     * PYTHON - Python表达式输入
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: [{ type: 'other', value: '' }]
     */
    case ATOM_FORM_TYPE.PYTHON:
      baseItem.formType = {
        type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.PYTHON}`,
      }
      baseItem.value = ''
      break

    /**
     * INPUT - 标准输入框
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: [{ type: 'other', value: '' }]
     */
    case ATOM_FORM_TYPE.INPUT:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.INPUT,
      }
      baseItem.value = ''
      break

    /**
     * CV_IMAGE - CV图片选择
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: [{ type: 'element', value: '' }]
     */
    case ATOM_FORM_TYPE.CV_IMAGE:
      baseItem.formType = {
        type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.CV_IMAGE}`,
      }
      baseItem.value = ''
      break

    /**
     * DATETIME - 日期时间选择
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: [{ type: 'other', value: '' }]
     */
    case ATOM_FORM_TYPE.DATETIME:
      baseItem.formType = {
        type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.DATETIME}`,
      }
      baseItem.value = ''
      break

    /**
     * COLOR - 颜色选择
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: [{ type: 'other', value: '' }]
     */
    case ATOM_FORM_TYPE.COLOR:
      baseItem.formType = {
        type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.COLOR}`,
      }
      baseItem.value = ''
      break

    /**
     * FILE - 文件选择
     * value格式: '
     * 默认值: ''
     * formType.params: { filters?: string[], file_type?: 'file' | 'folder' } - 非必填
     */
    case ATOM_FORM_TYPE.FILE:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.FILE,
        params: { filters: [], file_type: 'file' }, // 非必填
      }
      baseItem.value = ''
      break

    /**
     * TEXTAREAMODAL - 文本弹窗（多行输入）
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: [{ type: 'other', value: '' }]
     */
    case ATOM_FORM_TYPE.TEXTAREAMODAL:
      baseItem.formType = {
        type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.TEXTAREAMODAL}`,
      }
      baseItem.value = ''
      break

    /**
     * VARIABLE - 变量选择
     * value格式: Array<{ type: 'var', value: string }>
     * 默认值: [{ type: 'other', value: '' }]
     */
    case ATOM_FORM_TYPE.VARIABLE:
      baseItem.formType = {
        type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.VARIABLE}`,
      }
      baseItem.value = ''
      break

    /**
     * REMOTEFOLDERS - 远程文件夹选择
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: [{ type: 'other', value: '' }]
     */
    case ATOM_FORM_TYPE.REMOTEFOLDERS:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.REMOTEFOLDERS,
      }
      baseItem.value = ''
      break

    // ========== extraItem 类型（额外控件类型） ==========

    /**
     * PICK - 元素拾取
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: [{ type: 'other', value: '' }]
     * formType.params: { use?: 'WebPick' | 'WinPick' } - 非必填
     * 注意：PICK 需要联合 INPUT 才能正常工作，单独使用 PICK 无法更新 value
     */
    case ATOM_FORM_TYPE.PICK:
      baseItem.formType = {
        type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.PICK}`,
        params: { use: 'WebPick' }, // 非必填
      }
      baseItem.value = ''
      break

    /**
     * CVPICK - CV图片拾取
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: [{ type: 'element', value: '' }]
     */
    case ATOM_FORM_TYPE.CVPICK:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.CVPICK,
      }
      baseItem.value = ''
      break

    /**
     * GRID - 九宫格选择器
     * value格式: number (1-9)
     * 默认值: 1
     */
    case ATOM_FORM_TYPE.GRID:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.GRID,
      }
      baseItem.value = ''
      break

    /**
     * SLIDER - 滑块（用于CV相似度匹配等）
     * value格式: number (0-1 之间的小数，表示百分比，组件内部固定范围 0-100)
     * 默认值: 0.95 (表示 95%)
     */
    case ATOM_FORM_TYPE.SLIDER:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.SLIDER,
      }
      baseItem.value = ''
      break

    /**
     * CHECKBOX - 复选框
     * value格式: boolean
     * 默认值: false
     */
    case ATOM_FORM_TYPE.CHECKBOX:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.CHECKBOX,
      }
      baseItem.value = ''
      break

    /**
     * CHECKBOXGROUP - 复选框组
     * value格式: Array<any> (选中的值数组)
     * 默认值: []
     * options: Array<{ label: string, value: any }> - 必填
     */
    case ATOM_FORM_TYPE.CHECKBOXGROUP:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.CHECKBOXGROUP,
      }
      baseItem.value = ''
      baseItem.options = [ // 必填
        { label: '选项1', value: 'option1' },
        { label: '选项2', value: 'option2' },
        { label: '选项3', value: 'option3' },
      ]
      break

    /**
     * RADIO - 单选框
     * value格式: any (选中的值)
     * 默认值: ''
     * options: Array<{ label: string, value: any }> - 必填
     */
    case ATOM_FORM_TYPE.RADIO:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.RADIO,
      }
      baseItem.value = ''
      baseItem.options = [ // 必填
        { label: '选项1', value: 'option1' },
        { label: '选项2', value: 'option2' },
        { label: '选项3', value: 'option3' },
      ]
      break

    /**
     * SELECT - 下拉选择框
     * value格式: any (单选) 或 Array<any> (多选)
     * 默认值: 单选'' 多选 []
     * options: Array<{ label: string, value: any }> - 必填
     * formType.params: { multiple?: boolean } - 非必填，是否多选（默认 false）
     */
    case ATOM_FORM_TYPE.SELECT:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.SELECT,
        params: { multiple: false }, // 非必填
      }
      baseItem.value = '' // 多选类型需要默认值[], 否则显示错误
      baseItem.options = [ // 必填
        { label: '选项1', value: 'option1' },
        { label: '选项2', value: 'option2' },
        { label: '选项3', value: 'option3' },
      ]
      break

    /**
     * SWITCH - 开关
     * value格式: boolean
     * 默认值: false
     * options: Array<{ label: string, value: boolean }> - 必填，需要两个选项（开启/关闭）
     */
    case ATOM_FORM_TYPE.SWITCH:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.SWITCH,
      }
      baseItem.value = ''
      baseItem.options = [ // 必填
        { label: '开启', value: true },
        { label: '关闭', value: false },
      ]
      break

    /**
     * KEYBOARD - 键盘按键输入
     * value格式: string (按键名称)
     * 默认值: ''
     */
    case ATOM_FORM_TYPE.KEYBOARD:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.KEYBOARD,
      }
      baseItem.value = ''
      break

    /**
     * FONTSIZENUMBER - 字号数字输入框
     * value格式: number
     * 默认值: 14
     * min: number - 非必填，最小值（默认 8）
     * max: number - 非必填，最大值（默认 72）
     * step: number - 非必填，步长（默认 1）
     */
    case ATOM_FORM_TYPE.FONTSIZENUMBER:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.FONTSIZENUMBER,
      }
      baseItem.value = ''
      baseItem.min = 8 // 非必填
      baseItem.max = 72 // 非必填
      baseItem.step = 1 // 非必填
      break

    /**
     * MODALBUTTON - 弹窗按钮
     * value格式: string
     * 默认值: ''
     * formType.params: { loading?: boolean } - 非必填，是否显示加载状态（默认 false）
     */
    case ATOM_FORM_TYPE.MODALBUTTON:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.MODALBUTTON,
        params: { loading: false }, // 非必填
      }
      baseItem.value = ''
      break

    /**
     * DEFAULTDATEPICKER - 普通日期选择器
     * value格式: string (日期字符串，格式由 params.format 决定)
     * 默认值: ''
     * formType.params: { format?: string } - 非必填，日期格式（默认 'YYYY-MM-DD'）
     */
    case ATOM_FORM_TYPE.DEFAULTDATEPICKER:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.DEFAULTDATEPICKER,
        params: { format: 'YYYY-MM-DD' }, // 非必填
      }
      baseItem.value = ''
      break

    /**
     * RANGEDATEPICKER - 范围日期选择器
     * value格式: Array<string> (开始日期和结束日期的数组)
     * 默认值: []
     * formType.params: { format?: string } - 非必填，日期格式（默认 'YYYY-MM-DD'）
     */
    case ATOM_FORM_TYPE.RANGEDATEPICKER:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.RANGEDATEPICKER,
        params: { format: 'YYYY-MM-DD' }, // 非必填
      }
      baseItem.value = ''
      break

    /**
     * OPTIONSLIST - 选项列表（用于对话框选项等）
     * value格式: Array<{ rId: string, value: { rpa: 'special', value: Array<{ type: string, value: any }> } }>
     * 默认值: []
     */
    case ATOM_FORM_TYPE.OPTIONSLIST:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.OPTIONSLIST,
      }
      baseItem.value = ''
      break

    /**
     * DEFAULTPASSWORD - 普通密码输入框
     * value格式: string
     * 默认值: ''
     */
    case ATOM_FORM_TYPE.DEFAULTPASSWORD:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.DEFAULTPASSWORD,
      }
      baseItem.value = ''
      break

    /**
     * PROCESS_PARAM - 子流程配置参数
     * value格式: Array<{ varId: string, varName: string, varValue: { rpa: 'special', value: Array<any> } }>
     * 默认值: []
     * formType.params: { linkage?: string } - 非必填，联动字段的 key（用于获取子流程参数）
     */
    case ATOM_FORM_TYPE.PROCESS_PARAM:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.PROCESS_PARAM,
        params: { linkage: '' }, // 非必填
      }
      baseItem.value = ''
      break

    /**
     * FACTORELEMENT - 合同要素（元素选择 + 自定义元素控件）
     * value格式: { preset: string[], custom: Array<{ key: string, name: string, desc: string, example: string }> }
     * 默认值: { preset: [], custom: [] }
     * formType.params: { code?: number, options?: string[] } - 非必填
     *   - code: 1=只显示预置要素, 2=只显示自定义要素, 3=两个都显示（默认 3）
     *   - options: 预置要素选项列表（默认 []）
     */
    case ATOM_FORM_TYPE.FACTORELEMENT:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.FACTORELEMENT,
        params: { code: 3, options: [] }, // 非必填，options 默认为空数组
      }
      baseItem.value = ''
      break

    /**
     * CONTENTPASTE - 内容粘贴
     * value格式: Array<{ type: 'other' | 'python' | 'var', value: string }>
     * 默认值: ''
     */
    case ATOM_FORM_TYPE.CONTENTPASTE:
      baseItem.formType = {
        type: `${ATOM_FORM_TYPE.INPUT}_${ATOM_FORM_TYPE.CONTENTPASTE}`,
      }
      baseItem.value = ''
      break

    /**
     * MOUSEPOSITION - 鼠标位置拾取
     * value格式: string (坐标位置字符串)
     * 默认值: ''
     */
    case ATOM_FORM_TYPE.MOUSEPOSITION:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.MOUSEPOSITION,
      }
      baseItem.value = ''
      break

    /**
     * SCRIPTPARAMS - 脚本参数管理（JS脚本参数）
     * value格式: Array<{ varName: string, varValue: { rpa: 'special', value: Array<any> } }>
     * 默认值: []
     */
    case ATOM_FORM_TYPE.SCRIPTPARAMS:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.SCRIPTPARAMS,
      }
      baseItem.value = ''
      break

    /**
     * REMOTEPARAMS - 远程参数
     * value格式: string
     * 默认值: ''
     */
    case ATOM_FORM_TYPE.REMOTEPARAMS:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.REMOTEPARAMS,
      }
      baseItem.value = ''
      break

    /**
     * AIWORKFLOW - 选择AI工作流
     * value格式: { agentId: string, authId: number, inputs: Array<{ key: string, value: { rpa: 'special', value: any }, type: string }> }
     * 默认值: { agentId: '', authId: 0, inputs: [] }
     */
    case ATOM_FORM_TYPE.AIWORKFLOW:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.AIWORKFLOW,
      }
      baseItem.value = ''
      break

    default:
      baseItem.formType = {
        type: item.type,
      }
      baseItem.value = ''
  }

  return baseItem
}

// 所有表单类型列表
const allFormTypes = [
  // editItem 类型
  { type: ATOM_FORM_TYPE.PYTHON },
  { type: ATOM_FORM_TYPE.INPUT },
  // { type: ATOM_FORM_TYPE.ELEMENT }, // 已被删除
  { type: ATOM_FORM_TYPE.CV_IMAGE },
  { type: ATOM_FORM_TYPE.DATETIME },
  { type: ATOM_FORM_TYPE.COLOR },
  { type: ATOM_FORM_TYPE.FILE },
  { type: ATOM_FORM_TYPE.TEXTAREAMODAL },
  { type: ATOM_FORM_TYPE.VARIABLE },
  { type: ATOM_FORM_TYPE.REMOTEFOLDERS },
  // extraItem 类型
  { type: ATOM_FORM_TYPE.PICK },
  { type: ATOM_FORM_TYPE.CVPICK },
  { type: ATOM_FORM_TYPE.GRID },
  { type: ATOM_FORM_TYPE.SLIDER },
  { type: ATOM_FORM_TYPE.CHECKBOX },
  { type: ATOM_FORM_TYPE.CHECKBOXGROUP },
  { type: ATOM_FORM_TYPE.RADIO },
  { type: ATOM_FORM_TYPE.SELECT },
  { type: ATOM_FORM_TYPE.SWITCH },
  { type: ATOM_FORM_TYPE.KEYBOARD },
  { type: ATOM_FORM_TYPE.FONTSIZENUMBER },
  { type: ATOM_FORM_TYPE.MODALBUTTON },
  { type: ATOM_FORM_TYPE.DEFAULTDATEPICKER },
  { type: ATOM_FORM_TYPE.RANGEDATEPICKER },
  { type: ATOM_FORM_TYPE.OPTIONSLIST },
  { type: ATOM_FORM_TYPE.DEFAULTPASSWORD },
  { type: ATOM_FORM_TYPE.PROCESS_PARAM },
  { type: ATOM_FORM_TYPE.FACTORELEMENT },
  { type: ATOM_FORM_TYPE.CONTENTPASTE },
  { type: ATOM_FORM_TYPE.MOUSEPOSITION },
  { type: ATOM_FORM_TYPE.SCRIPTPARAMS },
  { type: ATOM_FORM_TYPE.AIWORKFLOW },
  { type: ATOM_FORM_TYPE.REMOTEPARAMS },
]

// 创建所有类型的表单示例
export const exampleFormList: RPA.AtomDisplayItem[] = allFormTypes.map((item, index) => createFormItemExample(item, index))

