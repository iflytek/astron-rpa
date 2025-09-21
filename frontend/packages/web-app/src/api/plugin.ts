import http from './http'
import { getRootBaseURL } from './http/env'

// 获取插件支持的浏览器
export async function getSupportBrowser() {
  const res = await http.get<{ browsers: string[] }>('/scheduler/browser/plugins/get_support', null, {
    baseURL: getRootBaseURL(),
    toast: false,
  })

  return res.data.browsers
}

// 浏览器插件查询状态
export function checkBrowerPlugin(browsers: string[]) {
  return http.post<Record<string, { installed: boolean, installed_version: string, latest: boolean }>>(
    '/scheduler/browser/plugins/check_status',
    { browsers },
    { baseURL: getRootBaseURL(), toast: false },
  )
}

// 浏览器插件安装
export function browerPluginInstall(params) {
  return http.post(
    '/scheduler/browser/plugins/install',
    {
      op: params.action, // 新增/更新
      browser: params.type,
    },
    { toast: false, baseURL: getRootBaseURL() },
  )
}

// 驱动插件查询状态
export function checkDriverPlugin() {
  return http.post('/tools/driver_check')
}

// 驱动插件安装
export function driverPluginInstall(params) {
  console.log(params)
  return Promise.resolve({ isOpen: false })
  // return http.post('/tools/driver_install', { ...params })
}

// Java插件查询状态
export function checkJavePlugin() {
  return http.post('/tools/java_check')
}

// Java插件安装
export function javePluginInstall(params) {
  console.log(params)

  // return http.post('/tools/java_install', { ...params })
  return Promise.resolve({
    results: [
      { exe_name: 'feishu', pid: 123 },
      { exe_name: 'java', pid: 12223 },
    ],
    msg: '',
    code: '000000',
  })
}
