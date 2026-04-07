import type { RequestConfig } from './http'

import http from './http'

/** 100 积分 = 1 元；前缀 `/api/rpa-additional`（文档默认 8005，网关转发） */
export const POINTS_PER_CNY = 100

const P = '/api/rpa-additional'

// --- 4.1 积分余额 ---

export interface PointsBalance {
  userPersonalBalance: number
  tenantRechargeBalance: number
  totalBalance: number
  tenantTotalBalance: number
  todayConsumption: number
  monthConsumption: number
  freeQuota: {
    weeklyTotal: number
    weeklyRemaining: number
    weeklyUsed: number
    resetTime: string
  }
}

export async function getPointsBalance() {
  const res = await http.get<PointsBalance>(`${P}/points/balance`)
  return res.data
}

// --- 4.2 消耗明细 GET /points/consumptions ---

export interface PointsConsumptionRecord {
  id: string
  consumedAt: string
  userId: string
  userName: string
  module: string
  provider: string
  unit: string
  unitAmount: number
  unitPrice: number
  points: number
  isFree: boolean
}

export interface PointsConsumptionParams {
  module?: string
  startDate?: string
  endDate?: string
  pageNo?: number
  pageSize?: number
}

export interface PointsConsumptionPage {
  todayConsumption: number
  monthConsumption: number
  records: PointsConsumptionRecord[]
  total: number
  pageNo: number
  pageSize: number
}

export async function getPointsConsumptions(
  params?: PointsConsumptionParams,
  config?: RequestConfig<PointsConsumptionPage>,
) {
  const res = await http.get<PointsConsumptionPage>(`${P}/points/consumptions`, params, config)
  return res.data
}

// --- 控制台：积分消耗柱状图 GET /console/points/consumption-bar ---

export type PointsConsumptionChartPeriod = 'today' | 'month'

export interface PointsConsumptionBarItem {
  label: string
  usedPoints: number
}

export interface PointsConsumptionBarData {
  period: PointsConsumptionChartPeriod
  totalUsed: number
  items: PointsConsumptionBarItem[]
}

export async function getPointsConsumptionBar(
  params: { period: PointsConsumptionChartPeriod },
  config?: RequestConfig<PointsConsumptionBarData>,
) {
  const res = await http.get<PointsConsumptionBarData>(`${P}/console/points/consumption-bar`, params, config)
  return res.data
}

// --- 控制台：积分消耗模块分布饼图 GET /console/points/consumption-pie ---

export interface PointsConsumptionPieItem {
  module: string
  usedPoints: number
}

export interface PointsConsumptionPieData {
  period: PointsConsumptionChartPeriod
  totalUsed: number
  items: PointsConsumptionPieItem[]
}

export async function getPointsConsumptionPie(
  params: { period: PointsConsumptionChartPeriod },
  config?: RequestConfig<PointsConsumptionPieData>,
) {
  const res = await http.get<PointsConsumptionPieData>(`${P}/console/points/consumption-pie`, params, config)
  return res.data
}

// --- 4.3 手动激活 POST /points/activate（一般无需调，balance 会自动激活）---

export async function postPointsActivate() {
  const res = await http.post<unknown>(`${P}/points/activate`, null)
  return res.data
}

// --- 4.4 商品列表 GET /payment/products（data 由交易服务透传）---

export interface PaymentProductsParams {
  type?: string
  pageNo?: number
  pageSize?: number
}

/** GET /payment/products 透传字段（与交易服务对齐，键名可能为小写） */
export interface PaymentProductItem {
  id: number
  versionid?: number
  versionId?: number
  name?: string
  price: number
  floorprice?: number
  type?: string
}

export async function getPaymentProducts(params?: PaymentProductsParams) {
  const res = await http.get<unknown>(`${P}/payment/products`, params)
  return res.data
}

// --- 4.5 创建充值订单 POST /payment/recharge ---

export interface PaymentRechargeBody {
  prodId: number
  versionId: number
  /** 100～10000000 且为 100 的倍数 */
  customPoints?: number
  channel: string
  clientIp?: string
}

export interface PaymentRechargeResult {
  bizorderno: string
  charge: string
}

export async function postPaymentRecharge(data: PaymentRechargeBody) {
  const res = await http.post<PaymentRechargeResult>(`${P}/payment/recharge`, data)
  return res.data
}

// --- 4.6 订单列表 GET /payment/orders ---

export interface PaymentOrdersParams {
  pageNo?: number
  pageSize?: number
  startDate?: string
  endDate?: string
  status?: string
}

/** 4.6 订单列表 data（字段以后端为准，可多传） */
export interface PaymentOrderRecord {
  bizorderno?: string
  orderNo?: string
  /** 支付渠道，如 alipay_qr */
  channel?: string
  subject?: string
  createdAt?: string
  paidAt?: string
  paymentStatus?: string
  /** 到账积分个数 */
  pointsAmount?: number
  /** 与积分同单位（积分个数），非人民币元；展示金额时需 ÷ POINTS_PER_CNY */
  realAmount?: number
  amount?: number
  payAmount?: number
  totalAmount?: number
  points?: number
  payPoints?: number
  payTime?: string
  gmtCreate?: string
  createTime?: string
  invoiceStatus?: string
  invoiceApplyStatus?: string
}

export interface PaymentOrdersPage {
  records: PaymentOrderRecord[]
  total: number
  pageNo?: number
  pageSize?: number
}

export async function getPaymentOrders(params?: PaymentOrdersParams) {
  const res = await http.get<PaymentOrdersPage>(`${P}/payment/orders`, params)
  return res.data
}

// --- 4.7 退款申请 POST /payment/refund ---

export interface PaymentRefundBody {
  bizorderno: string
  reason: string
}

export async function postPaymentRefund(data: PaymentRefundBody) {
  const res = await http.post<unknown>(`${P}/payment/refund`, data)
  return res.data
}

// --- 4.8 订单状态查询 GET /payment/order/status（轮询支付结果）---

export type PaymentOrderPaymentStatus = 'PAID' | 'PENDING' | string

export interface PaymentOrderStatusData {
  bizorderno: string
  paymentStatus: PaymentOrderPaymentStatus
  realAmount: number
  pointsAmount: number
  subject: string
  channel: string
  paidAt: string | null
  createdAt: string
}

export async function getPaymentOrderStatus(
  bizorderno: string,
  config?: RequestConfig<PaymentOrderStatusData>,
) {
  const res = await http.get<PaymentOrderStatusData>(
    `${P}/payment/order/status`,
    { bizorderno },
    { toast: false, ...config },
  )
  return res.data
}

// --- 开票申请 POST /points/orders/{bizorderno}/invoice ---

/** 发票类型（与交易/开票服务约定一致） */
export enum InvoiceType {
  /** 增值税普通发票 */
  GENERAL = 'GENERAL',
  /** 增值税专用发票 */
  VAT_SPECIAL = 'VAT_SPECIAL',
}

export interface PointsOrderInvoiceBody {
  invoiceTitle: string
  taxNumber: string
  invoiceType: InvoiceType
  email: string
}

export async function postPointsOrderInvoice(bizorderno: string, data: PointsOrderInvoiceBody) {
  const res = await http.post<unknown>(
    `${P}/points/orders/${encodeURIComponent(bizorderno)}/invoice`,
    data,
  )
  return res.data
}
