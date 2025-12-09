import { ErrorMessage, SuccessMessage } from './constant'
import { Utils } from './utils'

export const Cookie = {
  getCookie: (details: CookieDetails) => {
    return new Promise<unknown>((resolve) => {
      if (!details.url) {
        resolve(Utils.fail(ErrorMessage.PARAMS_URL_NOT_FOUND))
      }
      if (details.path) {
        details.domain = new URL(details.url).hostname
        delete details.url
      }
      else {
        delete details.path
      }
      chrome.cookies.getAll({ ...details }, (cookies) => {
        if (Array.isArray(cookies) && cookies.length) {
          resolve(Utils.success(cookies[0]))
        }
        else {
          resolve(Utils.success(null))
        }
      })
    })
  },

  removeCookie: (details: chrome.cookies.CookieDetails) => {
    return new Promise<unknown>((resolve) => {
      if (!details.url) {
        resolve(Utils.fail(ErrorMessage.PARAMS_URL_NOT_FOUND))
      }
      if (!details.name) {
        resolve(Utils.fail(ErrorMessage.PARAMS_NAME_NOT_FOUND))
      }
      chrome.cookies.remove(details, () => {
        resolve(Utils.success(SuccessMessage.DELETE_SUCCESS))
      })
    })
  },

  setCookies: (details: CookieDetails) => {
    return new Promise<unknown>((resolve) => {
      if (!details.url) {
        resolve(Utils.fail(ErrorMessage.PARAMS_URL_NOT_FOUND))
      }
      if (!details.name || !details.value) {
        resolve(Utils.fail(ErrorMessage.PARAMS_NAME_VALUE_NOT_FOUND))
      }
      chrome.cookies.set(details, () => {
        resolve(Utils.success(SuccessMessage.SET_SUCCESS))
      })
    })
  },
}
