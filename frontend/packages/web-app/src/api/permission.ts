import http from './http'

/**
 * 权限数据
 */
export function permission() {
  // return http.get('/robot/user/permission')
  const data = [
    {resource: 'designer'},
    {resource: 'actuator'},
    {resource: 'applicationMarket'},
    // {resource: 'admin'}
  ]
  return Promise.resolve({
    data: data.map(i=>{
      return {
        ...i,
        actions: ['all']
      }
    })
  })
}
