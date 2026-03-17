import http from '../http'

export function mobileLogin(params) {
  return http.post('uac/sys-login/login-by-code', null, { params })
}

export function rpaLoginPassWord(data: { phone: string, password: string }) {
  return http.post(
    '/uac/client/login',
    data,
    { loading: false },
  )
}

export function rpaGetSMSCode(data: { phone: string }) {
  return http.post('/uac/user/sms-code', data)
}

export function rpaRegister(data: { phone: string, password: string, code: string, confirmPassword: string }) {
  return http.post('/uac/user/register', data)
}

/**
 * @description: 登出
 */
export function rpaLogout(data: any) {
  return http.post('/uac/client/logout', data)
}

/**
 * @description: 获取租户空间列表
 */
export function getTenanList() {
  return http.get('/right/tenant/userinfo/getbyuser')
}

/**
 * 用户信息
 */
export function rpaUserInfo() {
  return http.post('/uac/user/user-info', {}, { toast: false })
}

/**
 * 回传用户选择的租户信息
 */
export function sendTenantId(data: { tenantId: string | number }) {
  return http.post('/right/tenant/select/client', data)
}

/**
 * 获取uuid
 */
export function getUUID(data: { phone: string }) {
  return http.get('/uac/sys-login/get/uuid', data)
}

/**
 * 发送短信验证码
 */
export function sendSMSCode(data: { phone: string }) {
  return http.post('/uac/sms/login-send', data)
}
