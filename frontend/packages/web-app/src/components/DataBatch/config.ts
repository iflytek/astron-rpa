/** @format */
import type { BatchDataTableMenu } from '@/types/databatch.d'

export const Menus: BatchDataTableMenu[] = [
  {
    key: 'editColumnName',
    label: '编辑列名',
    // showType: 'similar',
  },
  {
    key: 'copyColumn',
    label: '复制列',
    showType: 'similar',
  },
  {
    key: 'insertColumnLeft',
    label: '向左侧插入列',
    showType: 'similar',
  },
  {
    key: 'insertColumnRight',
    label: '向右侧插入列',
    showType: 'similar',
  },
  {
    key: 'similarAdd',
    label: '补充相似数据',
    showType: 'similar',
  },
  {
    key: 'editColumnElement',
    label: '编辑列元素',
    showType: 'similar',
  },
  {
    key: 'toggleColumnData',
    label: '切换列数据类型',
    showType: 'similar',
    children: [
      {
        key: 'text',
        label: '元素文本',
      },
      {
        key: 'href',
        label: '元素链接',
      },
      {
        key: 'src',
        label: '图片地址',
      },
    ],
  },
  {
    key: 'colDataProcessConfig',
    label: '列数据处理',
    children: [
      {
        key: 'ExtractNum',
        label: '提取数字',
        checkable: true,
        checked: false,
        modal: false,
        showEdit: false,
      },
      {
        key: 'Trim',
        label: '去除首尾空格',
        checkable: true,
        checked: false,
        modal: false,
        showEdit: false,
      },
      {
        key: 'Replace',
        label: '字符替换',
        checkable: true,
        checked: false,
        modal: true,
        showEdit: false,
      },
      {
        key: 'Prefix',
        label: '添加前缀',
        checkable: true,
        checked: false,
        modal: true,
        showEdit: false,
      },
      {
        key: 'Suffix',
        label: '添加后缀',
        checkable: true,
        checked: false,
        modal: true,
        showEdit: false,
      },
      {
        key: 'FormatTime',
        label: '时间格式化',
        checkable: true,
        checked: false,
        modal: true,
        showEdit: false,
      },
      {
        key: 'Regular',
        label: '正则表达式',
        checkable: true,
        checked: false,
        modal: true,
        showEdit: false,
      },
      {
        key: 'clear',
        label: '清除所有条件',
      },
    ],
    active: false,
  },
  {
    key: 'colFilterConfig',
    label: '列筛选',
    active: false,
  },
  {
    key: 'filterConfig',
    label: '表格筛选',
    active: false,
  },
  {
    key: 'deleteColumn',
    label: '删除列',
    showType: 'similar',
  },
]

export const webData = {
  version: '1',
  type: 'web',
  app: 'chrome',
  path: {
    xpath: {
      rpa: 'special',
      value: [
        {
          type: 'other',
          value: '//input[@id="su"]',
        },
      ],
    },
    cssSelector: {
      rpa: 'special',
      value: [
        {
          type: 'other',
          value: '#su',
        },
      ],
    },
    pathDirs: [
      {
        tag: 'input',
        checked: true,
        value: 'input',
        attrs: [
          {
            name: 'index',
            value: {
              rpa: 'special',
              value: [
                {
                  type: 'other',
                  value: '',
                },
              ],
            },
            checked: false,
            type: 0,
          },
          {
            name: 'id',
            value: {
              rpa: 'special',
              value: [
                {
                  type: 'other',
                  value: 'su',
                },
              ],
            },
            checked: true,
            type: 0,
          },
          {
            name: 'class',
            value: {
              rpa: 'special',
              value: [
                {
                  type: 'other',
                  value: 'bg s_btn btnhover',
                },
              ],
            },
            checked: false,
            type: 0,
          },
          {
            name: 'type',
            value: {
              rpa: 'special',
              value: [
                {
                  type: 'other',
                  value: 'submit',
                },
              ],
            },
            checked: false,
            type: 0,
          },
        ],
      },
    ],
    parentClass: 'bg s_btn_wr',
    tag: '提交按钮',
    text: '百度一下',
    url: {
      rpa: 'special',
      value: [
        {
          type: 'other',
          value: 'https://www.baidu.com/',
        },
      ],
    },
    shadowRoot: false,
    tabTitle: '百度一下，你就知道',
    tabUrl: 'https://www.baidu.com/',
    isFrame: false,
    frameId: 0,
    checkType: 'visualization',
    matchTypes: [],
  },
  picker_type: 'ELEMENT',
}

export const ColumnsKeys = [
  // 'field',
  // 'title',
  // 'dataIndex',
  'slots',
  // 'isTable',
  // 'app',
  // 'type',
  // 'version',
  'showOverflow',
  // 'values',
  'columnIndex',
  'width',
]

export const expSelectList = [
  {
    label: '数学',
    key: 'math',
    options: [
      { label: '等于', value: '==', key: 'equal' },
      { label: '不等于', value: '!=', key: 'notEqual' },
      { label: '小于等于', value: '<=', key: 'lessEqual' },
      { label: '大于等于', value: '>=', key: 'greaterEqual' },
      { label: '小于', value: '<', key: 'less' },
      { label: '大于', value: '>', key: 'greater' },
    ],
  },
  {
    label: '字符串',
    key: 'string',
    options: [
      { label: '为空', value: 'isnull', key: 'isNull' },
      { label: '不为空', value: 'notnull', key: 'notNull' },
      { label: '包含', value: 'contains', key: 'contains' },
      { label: '不包含', value: 'not_contains', key: 'notContains' },
      { label: '枚举', value: 'enumerate', key: 'enumerate' },
      { label: '以其开始', value: 'startswith', key: 'startsWith' },
      { label: '不以其开始', value: 'not_startswith', key: 'notStartsWith' },
      { label: '以其结束', value: 'endswith', key: 'endsWith' },
      { label: '不以其结束', value: 'not_endswith', key: 'notEndsWith' },
    ],
  },
  {
    label: '日期时间',
    key: 'datetime',
    options: [
      { label: '在该时间之前', value: 'time_befor', key: 'timeBefore' },
      { label: '在该时间之后', value: 'time_after', key: 'timeAfter' },
      { label: '在该时间段内', value: 'time_between', key: 'timeBetween' },
    ],
  },
]

export const dateSelectList = [
  { label: '原始格式', value: '', key: 'original' },
  { label: '%Y-%m-%d %H:%M:%S', value: '%Y-%m-%d %H:%M:%S', key: 'ymd_hms' },
  { label: '%Y/%m/%d %H:%M:%S', value: '%Y/%m/%d %H:%M:%S', key: 'y_m_d_hms' },
  { label: '%Y.%m.%d %H:%M:%S', value: '%Y.%m.%d %H:%M:%S', key: 'y.m.d_hms' },
  { label: '%Y年%m月%d日 %H:%M:%S', value: '%Y年%m月%d日 %H:%M:%S', key: 'ycn_mn_dn_hms' },
  { label: '%Y-%m-%dT%H:%M:%S', value: '%Y-%m-%dT%H:%M:%S', key: 'ymdThms' },
  { label: '%Y年%m月%d日 %H时%M分%S秒', value: '%Y年%m月%d日 %H时%M分%S秒', key: 'ycn_mn_dn_hms_cn' },
  { label: '%Y-%m-%d %H:%M', value: '%Y-%m-%d %H:%M', key: 'ymd_hm' },
  { label: '%Y/%m/%d %H:%M', value: '%Y/%m/%d %H:%M', key: 'y_m_d_hm' },
  { label: '%Y.%m.%d %H:%M', value: '%Y.%m.%d %H:%M', key: 'y.m.d_hm' },
  { label: '%Y年%m月%d日 %H:%M', value: '%Y年%m月%d日 %H:%M', key: 'ycn_mn_dn_hm' },
  { label: '%Y年%m月%d日 %H时%M分', value: '%Y年%m月%d日 %H时%M分', key: 'ycn_mn_dn_hm_cn' },
  { label: '%m-%d %H:%M:%S', value: '%m-%d %H:%M:%S', key: 'md_hms' },
  { label: '%m/%d %H:%M:%S', value: '%m/%d %H:%M:%S', key: 'm_d_hms' },
  { label: '%m.%d %H:%M:%S', value: '%m.%d %H:%M:%S', key: 'm.d_hms' },
  { label: '%m月%d日 %H:%M:%S', value: '%m月%d日 %H:%M:%S', key: 'mn_dn_hms' },
  { label: '%m月%d日 %H时%M分%S秒', value: '%m月%d日 %H时%M分%S秒', key: 'mn_dn_hms_cn' },
  { label: '%Y-%m-%d', value: '%Y-%m-%d', key: 'ymd' },
  { label: '%Y-%#m-%#d', value: '%Y-%#m-%#d', key: 'y_md' },
  { label: '%Y/%m/%d', value: '%Y/%m/%d', key: 'y_m_d' },
  { label: '%Y.%m.%d', value: '%Y.%m.%d', key: 'y.m.d' },
  { label: '%Y年%m月%d日', value: '%Y年%m月%d日', key: 'ycn_mn_dn' },
  { label: '%Y-%m', value: '%Y-%m', key: 'ym' },
  { label: '%Y/%m', value: '%Y/%m', key: 'y_m' },
  { label: '%Y.%m', value: '%Y.%m', key: 'y.m' },
  { label: '%Y年%m月', value: '%Y年%m月', key: 'ycn_mn' },
  { label: '%m-%d', value: '%m-%d', key: 'md' },
  { label: '%m/%d', value: '%m/%d', key: 'm_d' },
  { label: '%m.%d', value: '%m.%d', key: 'm.d' },
  { label: '%m月%d日', value: '%m月%d日', key: 'mn_dn' },
  { label: '%H:%M:%S', value: '%H:%M:%S', key: 'hms' },
  { label: '%H时%M分%S秒', value: '%H时%M分%S秒', key: 'hms_cn' },
  { label: '%H:%M', value: '%H:%M', key: 'hm' },
  { label: '%H时%M分', value: '%H时%M分', key: 'hm_cn' },
  { label: '%w （数字代表周日到周六）', value: '%w', key: 'week_num' },
  { label: '%j （数字代表一年中第几天）', value: '%j', key: 'day_of_year' },
  { label: '%W （数字代表一年中第几周）', value: '%W', key: 'week_of_year' },
]

const obj = {}
function aaa(data) {
  data.forEach((item) => {
    obj[item.key] = item.label
  })
}
aaa(dateSelectList)
