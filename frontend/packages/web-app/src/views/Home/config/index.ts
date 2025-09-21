/**
 *  主页的配置信息
 */

const ROBOT_SOURCE_LOCAL = '本地'
const ROBOT_SOURCE_OFFICIAL = '官方市场'
const ROBOT_SOURCE_TEAM = '企业市场'
const ROBOT_SOURCE_COMMANDER = '部署'
const ROBOT_SOURCE_TEXT = {
  [ROBOT_SOURCE_LOCAL]: '本地',
  [ROBOT_SOURCE_OFFICIAL]: '官方市场',
  [ROBOT_SOURCE_TEAM]: '企业市场',
  [ROBOT_SOURCE_COMMANDER]: '调度中心',
}

const ROBOT_TYPE_OPTIONS = [
  {
    value: 'finance',
    label: '财务',
  },
  {
    value: 'education',
    label: '教育',
  },
  {
    value: 'medical',
    label: '医疗',
  },
  {
    value: 'game',
    label: '游戏',
  },
  {
    value: 'E-commerce',
    label: '电商',
  },
  {
    value: 'stream',
    label: '直播',
  },
  {
    value: 'telecom',
    label: '电信',
  },
  {
    value: 'government',
    label: '政府/事业单位',
  },
  {
    value: 'manufacturing',
    label: '生产制造',
  },
  {
    value: 'construction',
    label: '建筑/地产',
  },
  {
    value: 'tobacco',
    label: '烟草',
  },
  {
    value: 'operation',
    label: '运营',
  },
  {
    value: 'personnel',
    label: '人事',
  },
  {
    value: 'city_service',
    label: '城市服务',
  },
  {
    value: 'car',
    label: '汽车业',
  },
  {
    value: 'new_energy',
    label: '新能源',
  },
  {
    value: 'other',
    label: '其他',
  },
]

export {
  ROBOT_SOURCE_LOCAL,
  ROBOT_SOURCE_OFFICIAL,
  ROBOT_SOURCE_TEAM,
  ROBOT_SOURCE_TEXT,
  ROBOT_TYPE_OPTIONS,
}
