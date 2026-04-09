import { ATOM_FORM_TYPE } from '@/constants/atom'

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
      type: ATOM_FORM_TYPE.AIWORKFLOW,
    },
    {
      type: ATOM_FORM_TYPE.REMOTEPARAMS,
    },
  ]
  return { extraItem, editItem }
}
