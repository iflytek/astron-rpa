export type PointsModalTabKey = 'manage' | 'consume' | 'order'

export const POINTS_MODAL_TABS: { key: PointsModalTabKey; label: string }[] = [
  { key: 'manage', label: '积分管理' },
  { key: 'consume', label: '消耗详情' },
  { key: 'order', label: '订单管理' },
]
