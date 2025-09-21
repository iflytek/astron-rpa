import { ATOM_FORM_TYPE } from '@/constants/atom'
import { getRealValue } from '@/views/Arrange/components/atomForm/hooks/usePreview'

// 自定义表单项排序
export function useFormItemSort() {
  const editItem = [
    {
      type: ATOM_FORM_TYPE.PYTHON,
    },
    {
      type: ATOM_FORM_TYPE.INPUT,
    },
    {
      type: ATOM_FORM_TYPE.ELEMENT,
    },
    {
      type: ATOM_FORM_TYPE.CV_IMAGE,
    },
    {
      type: ATOM_FORM_TYPE.DATETIME,
    },
    {
      type: ATOM_FORM_TYPE.COLOR,
    },
    {
      type: ATOM_FORM_TYPE.FILE,
    },
    {
      type: ATOM_FORM_TYPE.TEXTAREAMODAL,
    },
    {
      type: ATOM_FORM_TYPE.VARIABLE,
    },
    {
      type: ATOM_FORM_TYPE.REMOTEFOLDERS,
    },
  ]
  const extraItem = [
    {
      type: ATOM_FORM_TYPE.PICK,
    },
    {
      type: ATOM_FORM_TYPE.CVPICK,
    },
    {
      type: ATOM_FORM_TYPE.GRID,
    },
    {
      type: ATOM_FORM_TYPE.SLIDER,
    },
    {
      type: ATOM_FORM_TYPE.CHECKBOX,
    },
    {
      type: ATOM_FORM_TYPE.CHECKBOXGROUP,
    },
    {
      type: ATOM_FORM_TYPE.RADIO,
    },
    {
      type: ATOM_FORM_TYPE.SELECT,
    },
    {
      type: ATOM_FORM_TYPE.SWITCH,
    },
    {
      type: ATOM_FORM_TYPE.KEYBOARD,
    },
    {
      type: ATOM_FORM_TYPE.FONTSIZENUMBER,
    },
    {
      type: ATOM_FORM_TYPE.MODALBUTTON,
    },
    {
      type: ATOM_FORM_TYPE.DEFAULTDATEPICKER,
    },
    {
      type: ATOM_FORM_TYPE.RANGEDATEPICKER,
    },
    {
      type: ATOM_FORM_TYPE.OPTIONSLIST,
    },
    {
      type: ATOM_FORM_TYPE.DEFAULTPASSWORD,
    },
    {
      type: ATOM_FORM_TYPE.PROCESS_PARAM,
    },
    {
      type: ATOM_FORM_TYPE.FACTORELEMENT,
    },
    {
      type: ATOM_FORM_TYPE.CONTENTPASTE,
    },
    {
      type: ATOM_FORM_TYPE.MOUSEPOSITION,
    },
    {
      type: ATOM_FORM_TYPE.SCRIPTPARAMS,
    },
    {
      type: ATOM_FORM_TYPE.REMOTEPARAMS,
    },
  ]
  return { extraItem, editItem }
}

// 表单项是否必填
export function useFormItemRequired(item: RPA.AtomDisplayItem) {
  const { required, value: atomValue } = item
  if (!required)
    return required
  if (Array.isArray(atomValue)) {
    return atomValue.every(atomItem => Object.is(atomItem.value, ''))
  }
  if (typeof atomValue === 'boolean')
    return false
  if (atomValue === '')
    return true
  return false
}

// 表单长度限制提示
export function getLimitLengthTip(limitLength: Array<string | number>) {
  const [min, max] = limitLength
  if (['-1', 1].includes(min)) {
    return `不应大于${max}`
  }
  if (['-1', 1].includes(max)) {
    return `不应小于${min}`
  }
  return `应在${min}到${max}之间`
}

// 表单项是否符合长度限制
export function useFormItemLimitLength(item: RPA.AtomDisplayItem) {
  const { limitLength, value } = item
  if (!(limitLength && limitLength.length === 2))
    return true
  const atomValue = getRealValue(value)
  const [min, max] = limitLength // [-1, 16] 有最大长度限制 [4, -1] 有最小长度限制 [4, 16] 有最小最大长度限制
  if (['-1', 1].includes(min)) {
    return atomValue.length <= max
  }
  if (['-1', 1].includes(max)) {
    return atomValue.length >= min
  }
  return atomValue.length >= min && atomValue.length <= max
}
