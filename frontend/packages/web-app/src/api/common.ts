import http from './http'

// 举报AI生成内容
export function aiFeedback<T>(data: T) {
  return http.post('/api/robot/feedback/submit', data)
}
