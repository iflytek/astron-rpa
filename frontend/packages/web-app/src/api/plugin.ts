import http from './http'

// 获取插件支持的浏览器
export async function getSupportBrowser() {
  const res = await http.get<{ browsers: string[] }>('/scheduler/browser/plugins/get_support', null, {
    toast: false,
  })

  return res.data.browsers
}

// 浏览器插件查询状态
export function checkBrowerPlugin(browsers: string[]) {
  return http.post<Record<string, { installed: boolean, installed_version: string, latest: boolean }>>(
    '/scheduler/browser/plugins/check_status',
    { browsers },
    { toast: false },
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
    { toast: false },
  )
}

// 插件安装前浏览器是否正在运行的检测
export function checkBrowerRunning(params) {
  return http.post(
    '/scheduler/browser/plugins/check_running',
    {
      browser: params.type,
    },
    { toast: false },
  )
}
