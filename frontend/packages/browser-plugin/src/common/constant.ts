import { t } from '../i18n/index'

// Background constants
export const SUPPORTED_PROTOCOLS = ['http://', 'https://', 'file://', 'ftp://']
export const OLD_EXTENSION_IDS = ['dibfknoajiboamheempfppeapcedplgm', 'gfpcfabhkgenjcmjgnldmkhjieekeeea']
export const CURRENT_EXTENSION_ID = chrome.runtime.id
export const NATIVE_HOST_NAME = 'com.astronrpa.nativehost'
export const IGNORE_LOG_KEYS = ['getElement', 'contentInject', 'backgroundInject']
export const BROWSER_MAP = {
  '': '',
  'chrome': '$chrome$',
  'edge': '$edge$',
  'msedge': '$edge$',
  'firefox': '$firefox$',
  '360se': '$360se$',
  '360se6': '$360se$',
  'qqbrowser': '$qqbrowser$',
  '360chrome': '$360Chrome$',
  '360chromex': '$360ChromeX$',
  'quark': '$quark$',
  'doubao': '$Doubao$',
}

// Content constants
export const MAX_TEXT_LENGTH = 10
export const MAX_TEXT_INCLUDE_LENGTH = 64
export const MAX_ATTRIBUTE_LENGTH = 32
export const DEEP_SEARCH_TRIGGER = 5 * 1000
export const ELEMENT_SEARCH_TRIGGER = 0
export const SCROLL_TIMES = 20
export const SCROLL_DELAY = 1500
export const HIGHT_BOX_SHADOW = 'inset 0px 0px 0px 2px red;'
export const HIGH_LIGHT_BG = '#ff4d4f85'
export const HIGH_LIGHT_BORDER = '2px solid red'
export const HIGH_LIGHT_COLOR = 'red'
export const HIGH_LIGHT_DURATION = 3000
export const ASTRON_SW_NAME = 'Astron-Service-Worker'
export const FRAME_ELEMENT_TAGS = ['iframe', 'frame', 'object', 'embed']

export const SVG_NODETAGS = [
  'svg',
  'g',
  'defs',
  'symbol',
  'use',
  'image',
  'switch',
  'a',
  'text',
  'tspan',
  'textPath',
  'foreignObject',
  'rect',
  'circle',
  'ellipse',
  'line',
  'polyline',
  'polygon',
  'path',
  'animate',
  'animateMotion',
  'animateTransform',
  'set',
  'linearGradient',
  'radialGradient',
  'pattern',
  'clipPath',
  'mask',
  'filter',
  'feBlend',
  'feColorMatrix',
  'feComponentTransfer',
  'feComposite',
  'feConvolveMatrix',
  'feDiffuseLighting',
  'feDisplacementMap',
  'feFlood',
  'feGaussianBlur',
  'feImage',
  'feMerge',
  'feMorphology',
  'feOffset',
  'feSpecularLighting',
  'feTile',
  'feTurbulence',
  'feDistantLight',
  'fePointLight',
  'feSpotLight',
  'marker',
  'view',
  'metadata',
  'title',
  'desc',
]

export enum StatusCode {
  SUCCESS = '0000',
  UNKNOWN_ERROR = '5001',
  ELEMENT_NOT_FOUND = '5002',
  EXECUTE_ERROR = '5003',
  VERSION_ERROR = '5004',
}

export const ErrorMessage = {
  // Background errors
  get TAB_GET_ERROR() { return t('errors.tabGetError') },
  get ACTIVE_TAB_ERROR() { return t('errors.activeTabError') },
  get NUMBER_ID_ERROR() { return t('errors.numberIdError') },
  get FRAME_GET_ERROR() { return t('errors.frameGetError') },
  get CURRENT_TAB_UNSUPPORT_ERROR() { return t('errors.currentTabUnsupportError') },
  get NOT_SIMILAR_ELEMENT() { return t('errors.notSimilarElement') },
  get SIMILAR_NOT_FOUND() { return t('errors.similarNotFound') },
  get RELATIVE_ELEMENT_PARAMS_ERROR() { return t('errors.relativeElementParamsError') },
  get ELEMENT_NOT_FOUND() { return t('errors.elementNotFound') },
  get UNSUPPORT_ERROR() { return t('errors.unsupportError') },
  get PARAMS_URL_NOT_FOUND() { return t('errors.paramsUrlNotFound') },
  get PARAMS_NAME_NOT_FOUND() { return t('errors.paramsNameNotFound') },
  get PARAMS_NAME_VALUE_NOT_FOUND() { return t('errors.paramsNameValueNotFound') },
  get CONTEXT_NOT_FOUND() { return t('errors.contextNotFound') },
  get EXECUTE_ERROR() { return t('errors.executeError') },
  get DEBUGGER_TIMOUT() { return t('errors.debuggerTimeout') },
  get CONTENT_MESSAGE_ERROR() { return t('errors.contentMessageError') },
  // Content errors
  get ELEMENT_INFO_INCOMPLETE() { return t('errors.elementInfoIncomplete') },
  get ELEMENT_MULTI_FOUND() { return t('errors.elementMultiFound') },
  get ELEMENT_NOT_INPUT() { return t('errors.elementNotInput') },
  get ELEMENT_NOT_CHECKED() { return t('errors.elementNotChecked') },
  get ELEMENT_NOT_SELECT() { return t('errors.elementNotSelect') },
  get ELEMENT_NOT_TABLE() { return t('errors.elementNotTable') },
  get ELEMENT_PARENT_NOT_FOUND() { return t('errors.elementParentNotFound') },
  get ELEMENT_CHILD_NOT_FOUND() { return t('errors.elementChildNotFound') },
  get ELEMENT_CHILD_ORIGIN_NOT_FOUND() { return t('errors.elementChildOriginNotFound') },
  get UPDATE_TIP() { return t('errors.updateTip') },
}

export const SuccessMessage = {
  get DELETE_SUCCESS() { return t('success.deleteSuccess') },
  get SET_SUCCESS() { return t('success.setSuccess') },
  get EMPTY_SUCCESS() { return t('success.emptySuccess') },
}
