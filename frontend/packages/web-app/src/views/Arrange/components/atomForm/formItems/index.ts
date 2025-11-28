/**
 * 表单项注册
 * 原子能力的表单项有多种类型，需要根据类型注册不同的组件，所有的表单项类型在 ATOM_FORM_TYPE 中定义
 * 但是在原子能力的元数据描述中，不一定返回的都是 ATOM_FORM_TYPE 中的类型，由于历史原因，会有一些特殊情况
 * 1. 会有些用 _ 分割的复合类型，比如：INPUT_VARIABLE_PYTHON，就是由三个类型组合而成的
 * 2. ATOM_FORM_TYPE.RESULT 类型是这两种类型的组合：[ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.VARIABLE]
 * 3. ATOM_FORM_TYPE.CONTENTPASTE 类型是这四种类型的组合：[ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.PYTHON, ATOM_FORM_TYPE.VARIABLE, ATOM_FORM_TYPE.CONTENTPASTE]
 * 4. ATOM_FORM_TYPE.PICK 类型更特殊，formType.params.use 等于 'CV' 时，
 * 是这三种类型的组合：[ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.CV_IMAGE, ATOM_FORM_TYPE.CVPICK]，
 * 否则是这四种类型的组合：[ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.PICK, ATOM_FORM_TYPE.VARIABLE]
 */

import { Component } from 'vue'

import { ATOM_FORM_TYPE } from '@/constants/atom'
import { PICK_TYPE_CV } from '@/views/Arrange/config/atom'

import StrInput from './StrInput.vue'
import Input from './Input.vue'
import Python from './Python.vue'
import Variable from './Variable.vue'
import Radio from './Radio.vue'
import File from './File.vue'
import MousePosition from './MousePosition.vue'
import Select from './Select.vue'
import Checkbox from './Checkbox.vue'
import CheckboxGroup from './CheckboxGroup.vue'
import Switch from './Switch.vue'
import InputNumber from './InputNumber.vue'
import Datetime from './Datetime.vue'
import InputPassword from './InputPassword.vue'
import CvImage from './CvImage.vue'
import CvPick from './CvPick.vue'
import Slider from './Slider.vue'
import Grid from './Grid.vue'
import TextareaModal from './TextareaModal.vue'
import Color from './Color.vue'
import ContentPaste from './ContentPaste.vue'
import Pick from './Pick.vue'
import Keyboard from './Keyboard.vue'
import ModalButton from './ModalButton.vue'
import DatePicker from './DatePicker.vue'
import RangeDatePicker from './RangeDatePicker.vue'
import OptionsList from './OptionsList.vue'
import ProcessParam from './ProcessParam.vue'
import ScriptParams from './ScriptParams.vue'
import ContractElement from './ContractElement.vue' 

/**
 * 根据上面的 type 映射规则，返回对应的 ATOM_FORM_TYPE 类型
 */
export function getFormTypeArray(item: RPA.AtomDisplayItem): ATOM_FORM_TYPE[] {
  const formType = item?.formType?.type ?? ''

  if (formType === ATOM_FORM_TYPE.RESULT) {
    return [ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.VARIABLE]
  }

  if (formType === ATOM_FORM_TYPE.PICK) {
    return item.formType.params.use === PICK_TYPE_CV
      ? [ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.CV_IMAGE, ATOM_FORM_TYPE.CVPICK]
      : [ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.PICK, ATOM_FORM_TYPE.VARIABLE]
  }

  if (formType === ATOM_FORM_TYPE.CONTENTPASTE) {
    return [ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.PYTHON, ATOM_FORM_TYPE.VARIABLE, ATOM_FORM_TYPE.CONTENTPASTE]
  }

  return formType.split('_') as ATOM_FORM_TYPE[]
}


/**
 * 组件位置类型
 * - prefix: 放置在 input 的前缀位置
 * - suffix: 放置在 input 的后缀位置
 * - inline: 作为 input 的一部分，与 input 在同一层级
 * - addonBefore: 与 input 平行的位置（input 前面）
 * - addonAfter: 与 input 平行的位置（input 后面）
 */
export type ComponentPosition = 'prefix' | 'suffix' | 'inline' | 'addonBefore' | 'addonAfter'

export interface FormItemProps {
  item: RPA.AtomDisplayItem
  values?: Record<string, any>
}

export interface FormItemEmits {
  /** 值变化事件 */
  (e: 'update', key: string, value: any): void
}

export type FormItemRegisterWithType = FormItemRegister & {
  type: ATOM_FORM_TYPE
}

export interface FormItemRegister {
  /** 组件实例 */
  component: Component<FormItemProps>
  /** 组件位置，默认为 'inline' */
  position?: ComponentPosition
}

export const FORM_ITEM_REGISTER: Partial<Record<ATOM_FORM_TYPE, FormItemRegister>> = {
  [ATOM_FORM_TYPE.STR_INPUT]: {
    component: StrInput,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.INPUT]: {
    component: Input,
    position: 'inline',
  },
  [ATOM_FORM_TYPE.PYTHON]: {
    component: Python,
    position: 'prefix',
  },
  [ATOM_FORM_TYPE.VARIABLE]: {
    component: Variable,
    position: 'suffix',
  },
  [ATOM_FORM_TYPE.RADIO]: {
    component: Radio,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.FILE]: {
    component: File,
    position: 'suffix',
  },
  [ATOM_FORM_TYPE.MOUSEPOSITION]: {
    component: MousePosition,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.SELECT]: {
    component: Select,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.CHECKBOX]: {
    component: Checkbox,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.CHECKBOXGROUP]: {
    component: CheckboxGroup,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.SWITCH]: {
    component: Switch,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.FONTSIZENUMBER]: {
    component: InputNumber,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.DATETIME]: {
    component: Datetime,
    position: 'suffix',
  },
  [ATOM_FORM_TYPE.DEFAULTPASSWORD]: {
    component: InputPassword,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.CV_IMAGE]: {
    component: CvImage,
    position: 'suffix',
  },
  [ATOM_FORM_TYPE.CVPICK]: {
    component: CvPick,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.SLIDER]: {
    component: Slider,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.GRID]: {
    component: Grid,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.TEXTAREAMODAL]: {
    component: TextareaModal,
    position: 'suffix',
  },
  [ATOM_FORM_TYPE.COLOR]: {
    component: Color,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.CONTENTPASTE]: {
    component: ContentPaste,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.PICK]: {
    component: Pick,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.KEYBOARD]: {
    component: Keyboard,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.MODALBUTTON]: {
    component: ModalButton,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.DEFAULTDATEPICKER]: {
    component: DatePicker,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.RANGEDATEPICKER]: {
    component: RangeDatePicker,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.OPTIONSLIST]: {
    component: OptionsList,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.PROCESS_PARAM]: {
    component: ProcessParam,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.SCRIPTPARAMS]: {
    component: ScriptParams,
    position: 'addonAfter',
  },
  [ATOM_FORM_TYPE.FACTORELEMENT]: {
    component: ContractElement,
    position: 'addonAfter',
  },
}
