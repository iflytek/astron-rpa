import { t } from '../i18n/index'

export const MAX_TEXT_LENGTH = 10
export const MAX_TEXT_INCLUDE_LENGTH = 64
export const MAX_ATTRIBUTE_LENGTH = 32
export const DEEP_SEARCH_TRIGGER = 5 * 1000
export const ELEMENT_SEARCH_TRIGGER = 200
export const SCROLL_TIMES = 20
export const SCROLL_DELAY = 1500
export const HIGHT_BOX_SHADOW = 'inset 0px 0px 0px 2px red;'
export const HIGH_LIGHT_BG = '#ff4d4f85'
export const HIGH_LIGHT_BORDER = '2px solid red'
export const HIGH_LIGHT_COLOR = 'red'
export const HIGH_LIGHT_DURATION = 3000
export const ASTRON_SW_NAME = 'Astron-Service-Worker'
export enum StatusCode {
  SUCCESS = '0000',
  UNKNOWN_ERROR = '5001',
  ELEMENT_NOT_FOUND = '5002',
  EXECUTE_ERROR = '5003',
  VERSION_ERROR = '5004',
}

export const ErrorMessage = {
  get ELEMENT_INFO_INCOMPLETE() { return t('errors.elementInfoIncomplete') },
  get ELEMENT_NOT_FOUND() { return t('errors.elementNotFound') },
  get ELEMENT_MULTI_FOUND() { return t('errors.elementMultiFound') },
  get ELEMENT_NOT_INPUT() { return t('errors.elementNotInput') },
  get ELEMENT_NOT_CHECKED() { return t('errors.elementNotChecked') },
  get ELEMENT_NOT_SELECT() { return t('errors.elementNotSelect') },
  get ELEMENT_NOT_TABLE() { return t('errors.elementNotTable') },
  get UNSUPPORT_ERROR() { return t('errors.unsupportError') },
  get ELEMENT_PARENT_NOT_FOUND() { return t('errors.elementParentNotFound') },
  get ELEMENT_CHILD_NOT_FOUND() { return t('errors.elementChildNotFound') },
  get ELEMENT_CHILD_ORIGIN_NOT_FOUND() { return t('errors.elementChildOriginNotFound') },
  get UPDATE_TIP() { return t('errors.updateTip') },
}

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
