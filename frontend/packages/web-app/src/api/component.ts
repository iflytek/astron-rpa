import http from './http'

/**
 * @description: 发布组件
 */
export function publishComponent(data: {
  componentId: string
  nextVersion: string
  updateLog: string
  name: string
  icon: string
  introduction: string
}) {
  return http.post('/robot/component-version/create', data)
}

/**
 * @description: 获取组件下一个版本号
 */
export function getComponentNextVersion(params: {
  componentId: string
}) {
  return http.get('/robot/component-version/next-version', params)
}
