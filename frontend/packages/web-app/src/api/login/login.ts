import http from '../http'

export function mobileLogin(params) {
  return http.post('uac/sys-login/login-by-code', null, { params })
}

export function rpaLoginPassWord(data: { phone: string, password: string }) {
  return http.post(
    '/api/uac/client/login',
    data,
    { loading: false },
  )
}

export function rpaGetSMSCode(data: { phone: string }) {
  return http.post('/api/uac/user/sms-code', data)
}

export function rpaRegister(data: { phone: string, password: string, code: string, confirmPassword: string }) {
  return http.post('/api/uac/user/register', data)
}

/**
 * @description: 登出
 */
export function rpaLogout(data: any) {
  return http.post('/api/uac/client/logout', data)
}

/**
 * 用户信息
 */
export function rpaUserInfo() {
  return http.post('/api/uac/user/user-info', {}, { toast: false })
}

/**
 * 获取uuid
 */
export function getUUID(data: { phone: string }) {
  return http.get('/api/uac/sys-login/get/uuid', data)
}

/**
 * 发送短信验证码
 */
export function sendSMSCode(data: { phone: string }) {
  return http.post('/api/uac/sms/login-send', data)
}
