/** @format */
import http from './http'
// 邮箱列表
export function apiGetMailList(params: { pageNo: number, pageSize: number }) {
  return http.get('/robot/taskMail/page/list', params)
}

// 邮箱
export function apiSaveMail(params: {
  emailService: string
  emailProtocol: string
  emailServiceAddress: string
  port: string
  enableSSL: boolean
  emailAccount: string
  authorizationCode: string
}) {
  return http.post('/robot/taskMail/save', params)
}

// 删除邮箱
export function apiDeleteMail(params: { resourceId: string }) {
  return http.post('/robot/taskMail/delete', params)
}

// 邮箱检测
export function apiCheckEmail(data) {
  return http.post('/robot/taskMail/connect', data)
}

// 邮箱连通性校验
export function mailTest(data: { user_mail: string, user_authorization: string, mail_flag: string, custom_mail_server?: string, custom_mail_port?: string }) {
  return http.post('/schedule/mail/detect', data)
}
