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
        if (cookies.length === 1) {
          resolve(Utils.success(cookies[0]))
        }
        else {
          resolve(Utils.success(cookies))
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

  setCookies: (details: CookieDetails | CookieDetails[]) => {
    return new Promise<unknown>((resolve) => {
      if (Array.isArray(details)) {
        const arr = details.map((cookie) => {
          return new Promise<unknown>((resolve1) => {
            const { name, url, value } = cookie
            if (!url) {
              resolve(Utils.fail(ErrorMessage.PARAMS_URL_NOT_FOUND))
            }
            if (!name || !value) {
              resolve(Utils.fail(ErrorMessage.PARAMS_NAME_VALUE_NOT_FOUND))
            }
            chrome.cookies.set(cookie, () => {
              resolve1(true)
            })
          })
        })
        Promise.all(arr).then(() => {
          resolve(Utils.success(SuccessMessage.SET_SUCCESS))
        })
      }
      else {
        if (!details.url) {
          resolve(Utils.fail(ErrorMessage.PARAMS_URL_NOT_FOUND))
        }
        if (!details.name || !details.value) {
          resolve(Utils.fail(ErrorMessage.PARAMS_NAME_VALUE_NOT_FOUND))
        }
        chrome.cookies.set(details, () => {
          resolve(Utils.success(SuccessMessage.SET_SUCCESS))
        })
      }
    })
  },
}
