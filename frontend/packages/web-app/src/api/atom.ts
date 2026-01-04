import http from './http'

// 根据id和version获取原子能力的具体信息
export function getAbilityInfo(atomList: { key: string, version: string }[]) {
  // return http.post('/robot/atom/getByVersionList', { atomList })
  return new Promise((resolve) => {
    http.post('/robot/atom-new/list', { keys: atomList.map(i => i.key) }).then((res) => {
      const data = res.data || []
      const result = data.map((atom: any) => atom.atomContent)
      resolve(result)
    })
  })
}

// 获取原子能力左侧菜单数据
export async function getAtomsMeta(): Promise<RPA.AtomMetaData> {
  const res = await http.post('/robot/atom-new/tree')
  return JSON.parse(res.data)
}

// 获取扩展组件左侧菜单数据
export async function getModuleMeta(): Promise<RPA.AtomTreeNode[]> {
  const res = await http.post('/robot/atom-new/tree')
  const data = JSON.parse(res.data)
  return data.atomicTreeExtend ?? []
}

export function getTreeByParentKey(parentKey: string) {
  return http.post('/robot/atom/getListByParentKey', null, { params: { parentKey } })
}

export function getNewAtomDesc(key: string): Promise<{ data: RPA.Atom }> {
  // return http.post('/robot/atom/getLatestAtomByKey', null, { params: { key } })
  return new Promise((resolve) => {
    http.post('/robot/atom-new/list', { keys: [key] }).then((res) => {
      const atom = res.data && res.data.length > 0 ? res.data[0] : ''
      const { atomContent = '' } = atom
      resolve({ data: atomContent })
    })
  })
}

/**
 * 添加收藏
 */
export function addFavorite(data: { atomKey: string }) {
  return http.get('/robot/atomLike/create', data)
}
/**
 * 取消收藏
 */
export function removeFavorite(data: { likeId: string }) {
  return http.get('/robot/atomLike/cancel', data)
}
/**
 * 获取收藏列表
 */
export async function getFavoriteList() {
  const res = await http.get<RPA.AtomTreeNode[]>('/robot/atomLike/list')
  return res.data ?? []
}

/**
 * 获取组件列表
 */
export async function getComponentList(data: {
  robotId: string
  version?: number
}) {
  const res = await http.post<RPA.ComponentManageItem[]>('/robot/component/editing/list', { ...data, mode: 'EDIT_PAGE' })
  return res.data ?? []
}

/**
 * 获取原子能力的配置参数
 */
export async function getConfigParams(params: {
  robotId: string
  robotVersion?: string | number
  processId?: string
  moduleId?: string
  mode?: string
}) {
  const res = await http.post<RPA.ConfigParamData[]>('/robot/param/all', params)
  return res.data
}

/**
 * 新增原子能力的配置参数
 */
export async function createConfigParam(data: RPA.CreateConfigParamData) {
  const res = await http.post<string>('/robot/param/add', data)
  return res.data
}

/**
 * 删除原子能力的配置参数
 * @param id 参数id
 */
export function deleteConfigParam(id: string) {
  return http.post(`/robot/param/delete?id=${id}`)
}

/**
 * 更新原子能力的配置参数
 * @param data RPA.ConfigParamData
 */
export function updateConfigParam(data: RPA.ConfigParamData) {
  return http.post('/robot/param/update', data)
}

/**
 * 获取远程共享变量
 */
export function getRemoteParams() {
  return http.get('/robot/robot-shared-var/get-shared-var', {})
}

/**
 * 获取卓越中心文件管理共享文件列表
 */
export function getRemoteFiles(data?: { pageSize?: number, fileName?: string }) {
  return http.post('/robot/robot-shared-file/page', data)
}
