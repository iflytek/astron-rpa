// 窗口名称
export enum WINDOW_NAME {
  MAIN = 'main',
  BATCH = 'batch',
  RECORD = 'record',
  RECORD_MENU = 'record-menu',
  SMART_COMP_PICK_MENU = 'smart-comp-pick-menu',
}

// 画布底部操作栏默认高度
export const BOTTOM_BOOTLS_HEIGHT_DEFAULT = 48
// 画布底部操作栏展开后最小高度
export const BOTTOM_BOOTLS_HEIGHT_SIZE_MIN = 251
// 普通侧边栏宽度
export const COMMON_SIDER_WIDTH = 280

// localStorage key
export const ELEMENTS_TREE_EXPANDE_KEYS = 'elements_tree_expanded_keys'
export const IMAGES_TREE_EXPANDE_KEYS = 'images_tree_expanded_keys'

// 保存编辑器中打开的流程 key
export const PROCESS_OPEN_KEYS = 'process_open_keys'

// 画布左侧操作栏默认宽度
export const LEFT_BOOTLS_WIDTH_DEFAULT = 40
// 画布左侧操作栏最小宽度
export const LEFT_BOOTLS_WIDTH_SIZE_MIN = 200
// 画布左侧操作栏最大宽度
export const LEFT_BOOTLS_WIDTH_SIZE_MAX = 240

export const SUCCES_MSG = 'Success'
export const ERROR_MSG = 'Failed'

export const SUCCESS_CODES = ['200', '000000', 200, '0000']
export const ERROR_CODES = ['500', '5001', '1001']
export const UN_AUTHORIZED_CODES = ['302', '4001', '401', '403', '900005', '900001'] // 900005空间过期 900001被其他账号顶掉

export const VUE_APP_AUTH = 'http://dev.iflyrpa.private:31680/login/#/invite'
export const VUE_APP_COMMANDER = 'https://www.iflyrpa.com/admin/'
export const VUE_APP_HELP = 'https://www.iflyrpa.com/docs/'
