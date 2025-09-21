const storageType = 'localStorage' // default storage type
export const storage = {
  get(key: string, type: 'localStorage' | 'sessionStorage' = storageType) {
    return window[type].getItem(key)
  },
  set(key: string, value: any, type: 'localStorage' | 'sessionStorage' = storageType) {
    window[type].setItem(key, value)
  },
  remove(key: string, type: 'localStorage' | 'sessionStorage' = storageType) {
    window[type].removeItem(key)
  },
  clear(type: 'localStorage' | 'sessionStorage' = storageType) {
    window[type].clear()
  },
}

export function setLoginFromType(type: string) {
  storage.set('loginFromType', type)
}

export function setAccountXf(params) {
  storage.set('USERACCOUNTXF', JSON.stringify(params))
}

export function clearAccountXf() {
  storage.remove('USERACCOUNTXF')
}

export function getAccountXf(): Promise<{ userName: string, password: string }> {
  return new Promise((resolve) => {
    const accountXF = storage.get('USERACCOUNTXF')
    const res = accountXF ? JSON.parse(accountXF) : { userName: '', password: '' }
    resolve(res)
  })
}

export function setAccount(params) {
  storage.set('USERACCOUNT', JSON.stringify(params))
}

export function clearAccount() {
  storage.remove('USERACCOUNT')
}

export function getAccount(): Promise<{ userName: string, password: string }> {
  return new Promise((resolve) => {
    const account = storage.get('USERACCOUNT')
    const res = account ? JSON.parse(account) : { userName: '', password: '' }
    resolve(res)
  })
}

export function setUserName(params) {
  storage.set('USERNAME', params)
}
export function getUserName() {
  return storage.get('USERNAME')
}

export function setTempData(data: object) {
  storage.set('TEMPDATA', JSON.stringify(data))
}

export function getTempData() {
  return storage.get('TEMPDATA')
}
