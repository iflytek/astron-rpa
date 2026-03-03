import { t } from '../i18n/index'

export const SUPPORTED_PROTOCOLS = ['http://', 'https://', 'file://', 'ftp://']

export const OLD_EXTENSION_IDS = ['dibfknoajiboamheempfppeapcedplgm', 'gfpcfabhkgenjcmjgnldmkhjieekeeea']

export const CURRENT_EXTENSION_ID = chrome.runtime.id

export const NATIVE_HOST_NAME = 'com.astronrpa.nativehost'

export const IGNORE_LOG_KEYS = ['getElement', 'contentInject', 'backgroundInject']

export enum StatusCode {
  SUCCESS = '0000',
  UNKNOWN_ERROR = '5001',
  ELEMENT_NOT_FOUND = '5002',
  EXECUTE_ERROR = '5003',
  VERSION_ERROR = '5004',
}

export const ErrorMessage = {
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
}

export const SuccessMessage = {
  get DELETE_SUCCESS() { return t('success.deleteSuccess') },
  get SET_SUCCESS() { return t('success.setSuccess') },
  get EMPTY_SUCCESS() { return t('success.emptySuccess') },
}
