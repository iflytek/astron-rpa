import http from './http'

// 邮箱列表
export function apiGetMailList(params: { pageNo: number, pageSize: number }) {
  return http.get('/api/robot/taskMail/page/list', params)
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
  return http.post('/api/robot/taskMail/save', params)
}

// 删除邮箱
export function apiDeleteMail(params: { resourceId: string }) {
  return http.post('/api/robot/taskMail/delete', params)
}

// 邮箱检测
export function apiCheckEmail(data) {
  return http.post('/api/robot/taskMail/connect', data)
}
