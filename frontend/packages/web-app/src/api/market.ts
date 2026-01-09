import http from './http'
/**
 * @description: 获取团队列表
 */
export function getTeams() {
  return http.post('/robot/market-team/get-list')
}

/**
 * @description: 获取全部应用列表
 */
export function getAppCards(data) {
  return http.post('/robot/market-resource/get-all-app-list', data)
}

/**
 * @description: 创建团队
 * @params {type String} teamId 团队Id {type String} appId 应用Id
 */
export function newTeam(data) {
  return http.post('/robot/market-team/add', data)
}

/**
 * @description: 创建团队-数量校验
 */
export function checkMarketNum() {
  return http.get('/robot/quota/check-market-join', { toast: true })
}

/**
 * @description: 黄色密级的应用，获取时校验是否是部门内部人员
 */
export function canAchieveApp(data) {
  return http.post('/robot/application/use-permission-check', data, { toast: false })
}

/**
 * @description: 申请使用
 */
export function useApplication(data) {
  console.log('useApplication', data)
  return http.post('/robot/application/submit-use-application', data, { toast: false })
}

/**
 * @description: 获取应用
 */
export function obtainApp(data) {
  return http.post('/robot/market-resource/obtain', data, { toast: false })
}

/**
 * @description: 轮询应用更新状态
 */
export function getAppUpdateStatus(data) {
  return http.post('/robot/market-resource/app-update-check', data)
}

/**
 * @description: 获取市场应用详情
 */
export function getAppDetails(params: { marketId: string, appId: string }) {
  return http.get('/robot/market-resource/app-detail', params)
}

/**
 * @description: 删除应用
 */
export function deleteApp(params) {
  return http.get('/robot/market-resource/delete-app', params)
}

// 消息列表
export function messageList(data) {
  return http.post('/robot/notify/notify-List', data)
  // return new Promise((resolve) => {
  //   resolve({
  //     code: '000000',
  //     data: {
  //       records: [
  //         {
  //           id: 74,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 3,
  //           appName: null,
  //           marketId: '1933333718814470144',
  //         },
  //         {
  //           id: 75,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 1,
  //           appName: null,
  //           marketId: '1933333718814470145',
  //         },
  //         {
  //           id: 76,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 2,
  //           appName: null,
  //           marketId: '1933333718814470146',
  //         },
  //         {
  //           id: 749,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 4,
  //           appName: null,
  //           marketId: '1933333718814470144',
  //         },
  //         {
  //           id: 750,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 1,
  //           appName: null,
  //           marketId: '1933333718814470145',
  //         },
  //         {
  //           id: 768,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 2,
  //           appName: null,
  //           marketId: '1933333718814470146',
  //         },
  //         {
  //           id: 747,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 5,
  //           appName: null,
  //           marketId: '1933333718814470144',
  //         },
  //         {
  //           id: 756,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 1,
  //           appName: null,
  //           marketId: '1933333718814470145',
  //         },
  //         {
  //           id: 7645,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 2,
  //           appName: null,
  //           marketId: '1933333718814470146',
  //         },
  //         {
  //           id: 743,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 3,
  //           appName: null,
  //           marketId: '1933333718814470144',
  //         },
  //         {
  //           id: 751,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 1,
  //           appName: null,
  //           marketId: '1933333718814470145',
  //         },
  //         {
  //           id: 762,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 2,
  //           appName: null,
  //           marketId: '1933333718814470146',
  //         },
  //         {
  //           id: 80,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 3,
  //           appName: null,
  //           marketId: '1933333718814470144',
  //         },
  //         {
  //           id: 81,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 1,
  //           appName: null,
  //           marketId: '1933333718814470145',
  //         },
  //         {
  //           id: 80,
  //           messageInfo: '[zgq]邀请你加入团队市场：[嗯嗯],确认是否加入？',
  //           messageType: 'teamMarketInvite',
  //           createTime: '2025-06-13 09:21:17',
  //           operateResult: 2,
  //           appName: null,
  //           marketId: '1933333718814470146',
  //         },
  //       ],
  //       total: 1,
  //       size: 10,
  //       current: 1,
  //       orders: [],
  //       optimizeCountSql: true,
  //       hitCount: false,
  //       searchCount: true,
  //       pages: 1,
  //     },
  //     message: data,
  //   })
  // })
}

// 指定已读消息
export function setMessageReadById(params) {
  return http.get('/robot/notify/set-selected-notify-read', params)
}

// 一键已读
export function setAllRead() {
  return http.get('/robot/notify/set-all-notify-read', {})
}

// 加入团队
export function acceptJoinTeam(params) {
  return http.get('/robot/notify/accept-join-team', params)
}

// 拒绝团队
export function refuseJoinTeam(params) {
  return http.get('/robot/notify/reject-join-team', params)
}

// 获取市场信息
export function teamInfo(params) {
  return http.post('/robot/market-team/info', null, { params })
}

// 编辑市场信息
export function editTeamInfo(data) {
  return http.post('/robot/market-team/edit', data)
}

// 离开团队
export function leaveTeamMarket(data) {
  return http.post('/robot/market-team/leave', data)
}

// 解散团队
export function dissolveTeamMarket(data) {
  return http.post('/robot/market-team/dissolve', data)
}

// 成员列表
export function marketUserList(data) {
  return http.post('/robot/market-user/list', data)
}

// 设置用户角色
export function setUserRole(data) {
  return http.post('/robot/market-user/role', data)
}

// 移除用户角色
export function removeUserRole(data) {
  return http.post('/robot/market-user/delete', data)
}

// 查询邀请员工
export function getInviteUser(data) {
  return http.post('/robot/market-user/get/user', data)
}

// 移交所有权查询员工
export function getTransferUser(data) {
  return http.post('/robot/market-user/leave/user', data)
}

// 邀请员工
export function inviteMarketUser(data) {
  return http.post('/robot/market-user/invite', data)
}

export function generateInviteLink(data: { marketId: string, expireType: string }) {
  return http.post('/robot/market-invite/generate-invite-link', data)
}

export function resetInviteLink(data: { marketId: string, expireType: string }) {
  return http.post('/robot/market-invite/reset-invite-link', data)
}

// 应用获取为应用时重命名检测
export function checkAppToRobotName(params) {
  return http.get('/market-resource/robot-name-duplicated', params)
}

/**
 * @description: 市场-新增应用弹窗过滤列表
 */
export function getAppFilterLst(data) {
  return http.post('/market-resource/add/robot/list', data)
}

/**
 * @description: 市场-获取组织架构信息
 */
export function getCompanyInfo(data) {
  return http.post('/robot/market-user/dept/user', data)
}

/**
 * @description: 消息通知-是否有新消息
 */
export function getNewMessage() {
  return http.get('/robot/notify/hasNotify', null, { toast: false })
}

/**
 * @description: 附件下载
 * @params {type String} resourceType 资源类型 mode 模式 本地或云端 resourceName 资源名称
 */
export function appendixDownload(data: any) {
  return http.post('/robot/appendix/download', data)
}

/**
 * @description: 取消附件下载
 * @params {type String} resourceType 资源类型 mode 模式 本地或云端 resourceName 资源名称
 */
export function cancelAppendixDownload(data: any) {
  return http.post('/robot/download/cancel', data)
}

/**
 * @description: 获取已部署的账号列表
 */
export function getDeployedAccounts(data: any) {
  return http.post('/robot/market-resource/deployed-user', data)
}

/**
 * @description: 部署市场应用
 */
export function deployApp(data: any) {
  return http.post('/robot/market-resource/deploy', data)
}

/**
 * @description: 版本推送市场应用
 */
export function pushApp(data: any) {
  return http.post('/robot/market-resource/update/push', data)
}

/**
 * @description: 版本推送-历史版本列表查询
 */
export function getPushHistoryVersions(data: any) {
  return http.post('/robot/market-resource/update/version-list', data)
}

// 部署弹窗获取成员列表
export function unDeployUserList(data) {
  return http.post('/robot/market-user/undeploy-user', data)
}

// 分享到市场 是否需发起申请检查
export function releaseCheck(data) {
  return http.post('/robot/application/pre-release-check', data)
}

// 分享到市场 发起上架申请
export function releaseApplication(data) {
  return http.post('/robot/application/submit-release-application', data)
}

// 分享到市场 发起上架申请
export function releaseCheckWithPublish(data) {
  return http.post('/robot/application/pre-submit-after-publish-check', data)
}

// 重新发版后立即发起上架申请
export function releaseWithPublish(data) {
  return http.post('/robot/application/submit-after-publish', data)
}

// 获取应用市场我的申请列表
export function applicationList(params: any) {
  console.log('applicationList', params)
  return http.post('/robot/application/my-application-page-list', params)
}

// 获取应用市场我的申请列表-删除
export function deleteApplication(params: object) {
  console.log('deleteApplication', params)
  return http.post('/robot/application/my-application-delete', params)
}

// 获取应用市场我的申请列表-撤销
export function cancelApplication(params: object) {
  console.log('cancelApplication', params)
  return http.post('/robot/application/my-application-cancel', params)
}

// 获取市场应用所有分类
export async function getAllClassification() {
  return http.get('/robot/classification/list')
}
