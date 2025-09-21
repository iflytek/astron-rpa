export const SUPPORTED_PROTOCOLS = ['http://', 'https://', 'file://', 'ftp://']

export const IGNORE_KEYS = ['getElement', 'backgroundInject', 'contentInject']

export const V2_EXTENSION_ID = 'dibfknoajiboamheempfppeapcedplgm' // v2插件ID

export const V3_EXTENSION_ID = 'gfpcfabhkgenjcmjgnldmkhjieekeeea' // v3插件ID

export const CURRENT_EXTENSION_ID = chrome.runtime.id // 当前插件ID

export enum StatusCode {
  SUCCESS = '0000',
  UNKNOWN_ERROR = '5001', // 通用错误
  ELEMENT_NOT_FOUND = '5002', // 元素未找到
  EXECUTE_ERROR = '5003', // 执行错误
  VERSION_ERROR = '5004', // 版本错误
}
