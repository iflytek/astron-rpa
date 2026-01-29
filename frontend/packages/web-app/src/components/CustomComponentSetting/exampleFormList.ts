import { ATOM_FORM_TYPE } from '@/constants/atom'

// 创建表单示例的辅助函数
function createFormItemExample(item: { type: string }, index: number): RPA.AtomDisplayItem {
  const baseItem: RPA.AtomDisplayItem = {
    types: 'Any',
    key: `demo_${item.type.toLowerCase()}_${index}`,
    title: `${item.type} 示例`,
    tip: `这是 ${item.type} 类型的表单示例`,
    value: [],
  }

  switch (item.type) {
    // editItem 类型
    case ATOM_FORM_TYPE.PYTHON:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.PYTHON,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      baseItem.required = true
      break

    case ATOM_FORM_TYPE.INPUT:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.INPUT,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.ELEMENT:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.ELEMENT,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.CV_IMAGE:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.CV_IMAGE,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.DATETIME:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.DATETIME,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.COLOR:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.COLOR,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.FILE:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.FILE,
        params: { filters: [], file_type: 'file' },
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.TEXTAREAMODAL:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.TEXTAREAMODAL,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.VARIABLE:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.VARIABLE,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.REMOTEFOLDERS:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.REMOTEFOLDERS,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    // extraItem 类型
    case ATOM_FORM_TYPE.PICK: // 联合类型, 会被解析成[ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.ELEMENT, ATOM_FORM_TYPE.PICK, ATOM_FORM_TYPE.VARIABLE]或者[ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.CV_IMAGE, ATOM_FORM_TYPE.CVPICK]
      baseItem.formType = {
        type: ATOM_FORM_TYPE.PICK,
        params: { use: 'WebPick' },
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.CVPICK:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.CVPICK,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.GRID:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.GRID,
      }
      baseItem.value = ''
      break

    case ATOM_FORM_TYPE.SLIDER:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.SLIDER,
      }
      baseItem.value = 50
      baseItem.min = 0
      baseItem.max = 100
      baseItem.step = 1
      break

    case ATOM_FORM_TYPE.CHECKBOX:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.CHECKBOX,
      }
      baseItem.value = false
      baseItem.options = [
        { label: '是', value: true },
        { label: '否', value: false },
      ]
      break

    case ATOM_FORM_TYPE.CHECKBOXGROUP:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.CHECKBOXGROUP,
      }
      baseItem.value = []
      baseItem.options = [
        { label: '选项1', value: 'option1' },
        { label: '选项2', value: 'option2' },
        { label: '选项3', value: 'option3' },
      ]
      break

    case ATOM_FORM_TYPE.RADIO:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.RADIO,
      }
      baseItem.value = 'option1'
      baseItem.options = [
        { label: '选项1', value: 'option1' },
        { label: '选项2', value: 'option2' },
        { label: '选项3', value: 'option3' },
      ]
      break

    case ATOM_FORM_TYPE.SELECT:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.SELECT,
        params: { multiple: false },
      }
      baseItem.value = 'option1'
      baseItem.options = [
        { label: '选项1', value: 'option1' },
        { label: '选项2', value: 'option2' },
        { label: '选项3', value: 'option3' },
      ]
      break

    case ATOM_FORM_TYPE.SWITCH:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.SWITCH,
      }
      baseItem.value = false
      baseItem.options = [
        { label: '开启', value: true },
        { label: '关闭', value: false },
      ]
      break

    case ATOM_FORM_TYPE.KEYBOARD:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.KEYBOARD,
      }
      baseItem.value = ''
      break

    case ATOM_FORM_TYPE.FONTSIZENUMBER:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.FONTSIZENUMBER,
      }
      baseItem.value = 14
      baseItem.min = 8
      baseItem.max = 72
      baseItem.step = 1
      break

    case ATOM_FORM_TYPE.MODALBUTTON:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.MODALBUTTON,
        params: { loading: true },
      }
      baseItem.value = ''
      break

    case ATOM_FORM_TYPE.DEFAULTDATEPICKER:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.DEFAULTDATEPICKER,
        params: { format: 'YYYY-MM-DD' },
      }
      baseItem.value = ''
      break

    case ATOM_FORM_TYPE.RANGEDATEPICKER:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.RANGEDATEPICKER,
        params: { format: 'YYYY-MM-DD' },
      }
      baseItem.value = []
      break

    case ATOM_FORM_TYPE.OPTIONSLIST:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.OPTIONSLIST,
      }
      baseItem.value = []
      break

    case ATOM_FORM_TYPE.DEFAULTPASSWORD:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.DEFAULTPASSWORD,
      }
      baseItem.value = ''
      break

    case ATOM_FORM_TYPE.PROCESS_PARAM:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.PROCESS_PARAM,
        params: { linkage: '' },
      }
      baseItem.value = []
      break

    case ATOM_FORM_TYPE.FACTORELEMENT:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.FACTORELEMENT,
        params: { code: 3, options: ['要素1', '要素2', '要素3'] },
      }
      // FACTORELEMENT 的 value 需要是 JSON 字符串格式
      baseItem.value = JSON.stringify({ preset: [], custom: [] })
      break

    case ATOM_FORM_TYPE.CONTENTPASTE: // 联合类型, 会被解析成[ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.PYTHON, ATOM_FORM_TYPE.VARIABLE, ATOM_FORM_TYPE.CONTENTPASTE]
      baseItem.formType = {
        type: ATOM_FORM_TYPE.CONTENTPASTE,
      }
      baseItem.value = [{ type: 'other', value: '' }]
      break

    case ATOM_FORM_TYPE.MOUSEPOSITION:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.MOUSEPOSITION,
      }
      baseItem.value = ''
      break

    case ATOM_FORM_TYPE.SCRIPTPARAMS:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.SCRIPTPARAMS,
      }
      // SCRIPTPARAMS 的 value 需要是 JSON 字符串格式的数组
      baseItem.value = JSON.stringify([])
      break

    case ATOM_FORM_TYPE.REMOTEPARAMS:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.REMOTEPARAMS,
      }
      baseItem.value = ''
      break

    case ATOM_FORM_TYPE.AIWORKFLOW:
      baseItem.formType = {
        type: ATOM_FORM_TYPE.AIWORKFLOW,
      }
      baseItem.value = {
        agentId: '',
        authId: 0,
        inputs: [],
      } as any
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
  { type: ATOM_FORM_TYPE.ELEMENT },
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

