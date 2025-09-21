import { Utils } from './utils'

export const Cookie = {
  // 拿到cookies
  getCookie: (details: chrome.cookies.CookieDetails) => {
    return new Promise<unknown>((resolve) => {
      // 没有url
      if (!details.url) {
        resolve(Utils.fail('缺少url字段！'))
      }
      if (details.name) {
        chrome.cookies.get(details, (cookies) => {
          resolve(Utils.success(cookies))
        })
      }
      else {
        chrome.cookies.getAll({ url: details.url }, (cookies) => {
          resolve(Utils.success(cookies))
        })
      }
    })
  },
  // 删除cookie
  removeCookie: (details: chrome.cookies.CookieDetails) => {
    return new Promise<unknown>((resolve) => {
      if (!details.url) {
        resolve(Utils.fail('缺少url字段！'))
      }
      if (!details.name) {
        resolve(Utils.fail('缺少name字段！'))
      }
      chrome.cookies.remove(details, () => {
        resolve(Utils.success('删除成功'))
      })
    })
  },
  // 设置cookie
  setCookies: (details: CookieDetails | CookieDetails[]) => {
    return new Promise<unknown>((resolve) => {
      if (Array.isArray(details)) {
        const arr = details.map((cookie) => {
          return new Promise<unknown>((resolve1) => {
            const { name, url, path, value, domain, expirationDate } = cookie
            if (!url) {
              resolve(Utils.fail('缺少url字段！'))
            }
            if (!name || !value) {
              resolve(Utils.fail('缺少必填字段name, value！'))
            }
            const data = {
              name,
              value,
              url,
              domain,
              expirationDate,
              path,
            }
            chrome.cookies.set(data, () => {
              resolve1(true)
            })
          })
        })
        Promise.all(arr).then(() => {
          resolve(Utils.success('设置成功'))
        })
      }
      else {
        if (!details.url) {
          resolve(Utils.fail('缺少url字段！'))
        }
        if (!details.name || !details.value) {
          resolve(Utils.fail('缺少必填字段name, value！'))
        }
        chrome.cookies.set(details, () => {
          resolve(Utils.success('设置成功'))
        })
      }
    })
  },
}
