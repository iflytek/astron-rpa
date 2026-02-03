import type { ITableResponse } from '@/types/normalTable'

import http from './http'

/**
 * @description: 获取团队列表
 */
export async function getTeams() {
  const res = await http.post('/api/robot/market-team/get-list')
  return res.data || []
}

/**
 * @description: 获取全部应用列表
 */
export async function getAppCards(data) {
  const res = await http.post<ITableResponse>('/api/robot/market-resource/get-all-app-list', data)
  return res.data || { records: [], total: 0 }
}

/**
 * @description: 创建团队
 * @params {type String} teamId 团队Id {type String} appId 应用Id
 */
export function newTeam(data) {
  return http.post('/api/robot/market-team/add', data)
}

/**
 * @description: 创建团队-数量校验
 */
export function checkMarketNum() {
  return http.get('/api/robot/quota/check-market-join', { toast: true })
}

/**
 * @description: 黄色密级的应用，获取时校验是否是部门内部人员
 */
export function canAchieveApp(data) {
  return http.post('/api/robot/application/use-permission-check', data, { toast: false })
}

/**
 * @description: 申请使用
 */
export function useApplication(data) {
  console.log('useApplication', data)
  return http.post('/api/robot/application/submit-use-application', data, { toast: false })
}

/**
 * @description: 获取应用
 */
export function obtainApp(data) {
  return http.post('/api/robot/market-resource/obtain', data, { toast: false })
}

/**
 * @description: 轮询应用更新状态
 */
export async function getAppUpdateStatus(data) {
  const res = await http.post('/api/robot/market-resource/app-update-check', data)
  return res.data
}

/**
 * @description: 获取市场应用详情
 */
export function getAppDetails(params: { marketId: string, appId: string }) {
  return http.get('/api/robot/market-resource/app-detail', params)
}

/**
 * @description: 删除应用
 */
export function deleteApp(params) {
  return http.get('/api/robot/market-resource/delete-app', params)
}

// 消息列表
export async function messageList(data) {
  const res = await http.post<ITableResponse>('/api/robot/notify/notify-List', data)
  return res.data
}

// 指定已读消息
export async function setMessageReadById(params) {
  const res = await http.get('/api/robot/notify/set-selected-notify-read', params)
  return res.data
}

// 一键已读
export async function setAllRead() {
  const res = await http.get('/api/robot/notify/set-all-notify-read', {})
  return res.data
}

// 加入团队
export async function acceptJoinTeam(params) {
  const res = await http.get('/api/robot/notify/accept-join-team', params)
  return res.data
}

// 拒绝团队
export async function refuseJoinTeam(params) {
  const res = await http.get('/api/robot/notify/reject-join-team', params)
  return res.data
}

// 获取市场信息
export function teamInfo(params) {
  return http.post('/api/robot/market-team/info', null, { params })
}

// 编辑市场信息
export function editTeamInfo(data) {
  return http.post('/api/robot/market-team/edit', data)
}

// 离开团队
export function leaveTeamMarket(data) {
  return http.post('/api/robot/market-team/leave', data)
}

// 解散团队
export function dissolveTeamMarket(data) {
  return http.post('/api/robot/market-team/dissolve', data)
}

// 成员列表
export async function marketUserList(data) {
  const res = await http.post<ITableResponse>('/api/robot/market-user/list', data)
  return res.data || { records: [], total: 0 }
}

// 设置用户角色
export function setUserRole(data) {
  return http.post('/api/robot/market-user/role', data)
}

// 移除用户角色
export function removeUserRole(data) {
  return http.post('/api/robot/market-user/delete', data)
}

// 查询邀请员工
export async function getInviteUser(data) {
  const res = await http.post('/api/robot/market-user/get/user', data)
  return res.data
}

// 移交所有权查询员工
export async function getTransferUser(data) {
  const res = await http.post('/api/robot/market-user/leave/user', data)
  return res.data
}

// 邀请员工
export function inviteMarketUser(data) {
  return http.post('/api/robot/market-user/invite', data)
}

export function generateInviteLink(data: { marketId: string, expireType: string }) {
  return http.post('/api/robot/market-invite/generate-invite-link', data)
}

export function resetInviteLink(data: { marketId: string, expireType: string }) {
  return http.post('/api/robot/market-invite/reset-invite-link', data)
}

// 应用获取为应用时重命名检测
export function checkAppToRobotName(params) {
  return http.get('/api/market-resource/robot-name-duplicated', params)
}

/**
 * @description: 市场-新增应用弹窗过滤列表
 */
export function getAppFilterLst(data) {
  return http.post('/api/market-resource/add/robot/list', data)
}

/**
 * @description: 市场-获取组织架构信息
 */
export function getCompanyInfo(data) {
  return http.post('/api/robot/market-user/dept/user', data)
}

/**
 * @description: 消息通知-是否有新消息
 */
export async function getNewMessage() {
  const res = await http.get('/api/robot/notify/hasNotify', null, { toast: false })
  return res.data
}

/**
 * @description: 附件下载
 * @params {type String} resourceType 资源类型 mode 模式 本地或云端 resourceName 资源名称
 */
export function appendixDownload(data: any) {
  return http.post('/api/robot/appendix/download', data)
}

/**
 * @description: 取消附件下载
 * @params {type String} resourceType 资源类型 mode 模式 本地或云端 resourceName 资源名称
 */
export function cancelAppendixDownload(data: any) {
  return http.post('/api/robot/download/cancel', data)
}

/**
 * @description: 获取已部署的账号列表
 */
export async function getDeployedAccounts(data: any) {
  const res = await http.post<ITableResponse>('/api/robot/market-resource/deployed-user', data)
  return res.data || { records: [], total: 0 }
}

/**
 * @description: 部署市场应用
 */
export function deployApp(data: any) {
  return http.post('/api/robot/market-resource/deploy', data)
}

/**
 * @description: 版本推送市场应用
 */
export function pushApp(data: any) {
  return http.post('/api/robot/market-resource/update/push', data)
}

/**
 * @description: 版本推送-历史版本列表查询
 */
export async function getPushHistoryVersions(data: any) {
  const res = await http.post('/api/robot/market-resource/update/version-list', data)
  return res.data
}

// 部署弹窗获取成员列表
export async function unDeployUserList(data) {
  const res = await http.post('/api/robot/market-user/undeploy-user', data)
  return res.data
}

// 分享到市场 是否需发起申请检查
export function releaseCheck(data) {
  return http.post('/api/robot/application/pre-release-check', data)
}

// 分享到市场 发起上架申请
export function releaseApplication(data) {
  return http.post('/api/robot/application/submit-release-application', data)
}

// 分享到市场 发起上架申请
export function releaseCheckWithPublish(data) {
  return http.post('/api/robot/application/pre-submit-after-publish-check', data)
}

// 重新发版后立即发起上架申请
export function releaseWithPublish(data) {
  return http.post('/api/robot/application/submit-after-publish', data)
}

// 获取应用市场我的申请列表
export function applicationList(params: any) {
  return http.post('/api/robot/application/my-application-page-list', params)
}

// 获取应用市场我的申请列表-删除
export function deleteApplication(params: object) {
  return http.post('/api/robot/application/my-application-delete', params)
}

// 获取应用市场我的申请列表-撤销
export function cancelApplication(params: object) {
  return http.post('/api/robot/application/my-application-cancel', params)
}

// 获取市场应用所有分类
export async function getAllClassification() {
  return http.get('/api/robot/classification/list')
}
