export const MAX_TEXT_LENGTH = 7 // text 最大文字数
export const DEEP_SEARCH_TRIGGER = 5 * 1000 // 深度搜索触发时间 ms
export const ELEMENT_SEARCH_TRIGGER = 200 // 元素搜索触发时间 ms
export const SCROLL_TIMES = 20 // 最大滚动搜索次数
export const SCROLL_DELAY = 1500 // 滚动延迟时间 ms
export const HIGHT_BOX_SHADOW = 'inset 0px 0px 0px 2px red;' // 内边框
export const HIGH_LIGHT_BG = '#ff4d4f85' // 高亮背景色
export const HIGH_LIGHT_BORDER = '2px solid red' // 高亮边框
export const HIGH_LIGHT_COLOR = 'red' // 高亮颜色
export const HIGH_LIGHT_DURATION = 3000 // 高亮持续时间 ms
export enum StatusCode {
  SUCCESS = '0000',
  UNKNOWN_ERROR = '5001', // 通用错误
  ELEMENT_NOT_FOUND = '5002', // 元素未找到
  EXECUTE_ERROR = '5003', // 执行错误
  VERSION_ERROR = '5004', // 版本错误
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
