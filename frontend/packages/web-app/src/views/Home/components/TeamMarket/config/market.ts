export const MARKET_USER_OWNER = 'owner'
export const MARKET_USER_ADMIN = 'admin'
export const MARKET_USER_COMMON = 'acquirer'
export const MARKET_USER_DEVELOPER = 'author'
export const MARKET_TYPE_PUBLIC = 'public'
export const MARKET_TYPE_TEAM = 'team'

export const USER_TYPES = [
  {
    key: MARKET_USER_OWNER,
    name: '所有者',
  },
  {
    key: MARKET_USER_ADMIN,
    name: '管理员',
  },
  {
    key: MARKET_USER_DEVELOPER,
    name: '开发者',
  },
  {
    key: MARKET_USER_COMMON,
    name: '获取者',
  },
]

export const FIRETEAM = '解散团队'
export const LEAVETEAM = '离开团队'
export const GIVETEAM = '移交所有权'
export const INVITEMEMBER = '邀请成员'

export const MARKET_APPSTATUS_TOOBTAIN = 'toObtain'
export const MARKET_APPSTATUS_OBTAINING = 'obtaining'
export const MARKET_APPSTATUS_OBTAINED = 'obtained'
export const MARKET_APPSTATUS_TOUPDATE = 'toUpdate'
export const MARKET_APPSTATUS_UPDATING = 'updating'

export const PENDING = 'pending'
export const REJECTED = 'rejected'
export const APPROVED = 'approved'
export const CANCELED = 'canceled'
export const applicationStatusMap = {
  [PENDING]: '待审核',
  [REJECTED]: '未通过',
  [APPROVED]: '已通过',
  [CANCELED]: '已撤销',
}
export const applicationStatus = [PENDING, REJECTED, APPROVED, CANCELED].map((status) => {
  return {
    label: applicationStatusMap[status],
    value: status,
  }
})

export const SECURITY_RED = 'red'
export const SECURITY_YELLOW = 'yellow'
export const SECURITY_GREEN = 'green'
export const SECURITY_LEVEL_TEXT = {
  [SECURITY_GREEN]: '公开',
  [SECURITY_YELLOW]: '内部',
  [SECURITY_RED]: '机密',
}
