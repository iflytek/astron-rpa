/**
 * 定义常量
 */
import { ATOM_KEY_MAP } from '@/constants/atom'

export const DISABLED_BREAKPOINT_TYPE = [
  ATOM_KEY_MAP.Group,
  ATOM_KEY_MAP.GroupEnd,
  ATOM_KEY_MAP.IfEnd,
  ATOM_KEY_MAP.ElseIfEnd,
  ATOM_KEY_MAP.ElseEnd,
  // 'endloop',
  ATOM_KEY_MAP.WhileEnd,
  ATOM_KEY_MAP.ForStepEnd,
  ATOM_KEY_MAP.ForListEnd,
  ATOM_KEY_MAP.ForDictEnd,
  ATOM_KEY_MAP.ForEnd,
  ATOM_KEY_MAP.TryEnd,
  ATOM_KEY_MAP.CatchEnd,
  ATOM_KEY_MAP.FinallyEnd,
  ATOM_KEY_MAP.Else,
  ATOM_KEY_MAP.Try,
  ATOM_KEY_MAP.Catch,
  ATOM_KEY_MAP.Finally,
  ATOM_KEY_MAP.Break,
  ATOM_KEY_MAP.Continue,
]
export const PAGE_INIT_INDENT = 82
export const PAGE_LEVEL_INDENT = 25
export const RECORDER_INIT_INDENT = 72
export const RECORDER_LEVEL_INDENT = 25

export const FLOW_DISABLE = 'disable'
export const FLOW_ACTIVE = 'active'
export const FLOW_DEBUGGING = 'debugging'
export const FLOW_FORBID = 'forbid'
export const DEFAULT_DESC_TEXT = '--'

export const SPECIALKEY = '丨丨丨丨'

export const defaultValueText = '<p><br></p>' // 富文本框标签
export const elementTag = 'e.' // 元素标签

export const CONDITION_OPTIONS_EXCEL_TYPE = [
  {
    label: '等于',
    operator: '==',
    value: '==',
  },
  {
    label: '不等于',
    operator: '!=',
    value: '!=',
  },
  {
    label: '开头是',
    operator: 'startswith',
    value: 'startswith',
    // value: 'SpiffWorkflow.operators.Equal'
  },
  {
    label: '开头不是',
    operator: 'not_startswith',
    value: 'not_startswith',
    // value: 'SpiffWorkflow.operators.NotEqual'
  },
  {
    label: '结尾是',
    operator: 'endswith',
    value: 'endswith',
    // value: 'SpiffWorkflow.operators.Equal'
  },
  {
    label: '结尾不是',
    operator: 'not_endswith',
    value: 'not_endswith',
    // value: 'SpiffWorkflow.operators.NotEqual'
  },
  {
    label: '包含',
    operator: 'contains',
    value: 'contains',
    // value: 'SpiffWorkflow.operators.Match'
  },
  {
    label: '不包含',
    operator: 'not_contains',
    value: 'not_contains',
    // value: 'SpiffWorkflow.operators.NotMatch'
  },
  {
    label: '大于',
    operator: '>',
    value: '>',
    // value: 'SpiffWorkflow.operators.GreaterThan',
  },
  {
    label: '大于等于',
    operator: '>=',
    value: '>=',
    // value: 'SpiffWorkflow.operators.GreaterThan',
  },
  {
    label: '小于',
    operator: '<',
    value: '<',
    // value: 'SpiffWorkflow.operators.LessThan'
  },
  {
    label: '小于等于',
    operator: '<=',
    value: '<=',
    // value: 'SpiffWorkflow.operators.LessThan'
  },
  {
    label: '为空',
    operator: 'isnull',
    value: 'isnull',
  },
  {
    label: '不为空',
    operator: 'notnull',
    value: 'notnull',
  },
]

export const CONDITION_OPTIONS_DATAFRAME_TYPE = [
  {
    label: '等于',
    operator: '==',
    value: '==',
  },
  {
    label: '不等于',
    operator: '!=',
    value: '!=',
  },
  {
    label: '开头是',
    operator: 'startswith',
    value: 'startswith',
  },
  {
    label: '开头不是',
    operator: 'not_startswith',
    value: 'not_startswith',
  },
  {
    label: '结尾是',
    operator: 'endswith',
    value: 'endswith',
  },
  {
    label: '结尾不是',
    operator: 'not_endswith',
    value: 'not_endswith',
  },
  {
    label: '包含',
    operator: 'contains',
    value: 'contains',
  },
  {
    label: '不包含',
    operator: 'not_contains',
    value: 'not_contains',
  },
  {
    label: '大于',
    operator: '>',
    value: '>',
  },
  {
    label: '大于等于',
    operator: '>=',
    value: '>=',
  },
  {
    label: '小于',
    operator: '<',
    value: '<',
  },
  {
    label: '小于等于',
    operator: '<=',
    value: '<=',
  },
  {
    label: '枚举',
    operator: 'enumerate',
    value: 'enumerate',
  },
  {
    label: '为空',
    operator: 'isnull',
    value: 'isnull',
  },
  {
    label: '不为空',
    operator: 'notnull',
    value: 'notnull',
  },
]
