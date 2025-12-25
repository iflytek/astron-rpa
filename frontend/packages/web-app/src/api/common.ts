import http from './http'

// 举报AI生成内容
export const aiFeedback = <T>(data: T) => {
  return http.post('/rpa-auth/feedback/submit', data)
}
