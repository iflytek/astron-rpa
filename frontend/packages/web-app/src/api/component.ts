import http from './http'
import { getRootBaseURL } from './http/env'

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

/**
 * @description: 将AI生成的代码转换成智能组件原子能力信息
 */
export async function codeToMeta(data: { code: string }) {
  const res = await http.post('/scheduler/smart/code-to-meta', data, { baseURL: getRootBaseURL() })
  return res.data
}

/**
 * @description: 智能组件存储
 */
export async function saveSmartComp(data) {
  const res = await http.post('/robot/smart/save', data)
  return res.data.smartId as string
}

/**
 * @description: 智能组件读取
 */
export async function getSmartComp(data: { robotId: string, smartId: string }) {
  const res = await http.post<RPA.Atom>('/robot/smart/detail/all', data)
  return res.data
}

/**
 * @description: 优化提问
 */
export async function optimizeQuestion(data: {
  sceneCode: string
  user: string
  elements: any[]
}) {
  const res = await http.post<RPA.Atom>('/rpa-ai-service/smart/chat', { ...data, chatHistory: [] })
  return res.data?.choices?.[0]?.message?.content || ''
}
// 返回值示例：
// ```new_prompt
// 在`{块元素_AI写作_8:1993287190512476160}`中完成可见元素的自动化操作

// 操作步骤：
// 1. 点击`{块元素_AI写作_8:1993287190512476160}`，触发AI写作功能
// 2. 等待`{AI写作功能面板}`展开或加载完成
// 3. 在展开的`{AI写作功能面板}`中，完成`[具体操作内容]`（如：输入写作主题、选择写作类型、点击生成按钮等）

// 注意：
// 1. 确保`{块元素_AI写作_8:1993287190512476160}`处于可点击状态
// 2. 点击后需等待面板完全加载，避免后续操作失败
// 3. 请根据实际需求补充`[具体操作内容]`的详细步骤
// ```
