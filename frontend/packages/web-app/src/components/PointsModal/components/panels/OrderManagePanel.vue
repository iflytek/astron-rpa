<script setup lang="ts">
import { CalendarOutlined } from '@ant-design/icons-vue'
import type { Dayjs } from 'dayjs'
import type { ColumnsType } from 'ant-design-vue/es/table'
import { Table } from 'ant-design-vue'
import { useResizeObserver } from '@vueuse/core'
import { computed, h, nextTick, onMounted, ref, watch } from 'vue'

import type { PaymentOrderRecord } from '@/api/points'
import { getPaymentOrders, POINTS_PER_CNY } from '@/api/points'

import InvoiceApplyModal from '../InvoiceApplyModal.vue'

type OrderActionType = 'apply' | 'invoicing' | 'applied' | 'applied_proxy'

interface OrderRow {
  key: string
  orderId: string
  subject: string
  channel: string
  amountYuan: number
  points: number
  createdAt: string
  paidAt: string
  /** 后端 paymentStatus 原始值，用于中文与颜色映射 */
  paymentStatusRaw: string
  action: OrderActionType
}

function mapInvoiceToAction(inv: string): OrderActionType {
  const s = inv.toLowerCase()
  if (s.includes('proxy') || s === 'agency' || s === 'applied_proxy')
    return 'applied_proxy'
  if (s.includes('ing') || s === 'processing' || s === 'invoicing')
    return 'invoicing'
  if (s.includes('applied') || s === 'done' || s === 'success' || s === 'issued')
    return 'applied'
  return 'apply'
}

const CHANNEL_LABELS: Record<string, string> = {
  alipay_qr: '支付宝扫码',
  alipay: '支付宝',
  wechat: '微信',
  wechat_native: '微信扫码',
}

function formatChannel(raw: string): string {
  const s = raw.trim()
  if (!s)
    return '—'
  return CHANNEL_LABELS[s] ?? s
}

/** 后端 paymentStatus → 中文文案 + 文字颜色（含 dark） */
function getPaymentStatusDisplay(raw: string): { label: string; className: string } {
  const k = raw.trim().toUpperCase()
  if (!k) {
    return {
      label: '—',
      className:
        'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]',
    }
  }

  const map: Record<string, { label: string; className: string }> = {
    PAID: {
      label: '已支付',
      className:
        'text-sm font-medium leading-[22.4px] text-[#52c41a] dark:text-[#73d13d]',
    },
    PENDING: {
      label: '待支付',
      className:
        'text-sm font-normal leading-[22.4px] text-[#fa8c16] dark:text-[#ffa940]',
    },
    UNPAID: {
      label: '未支付',
      className:
        'text-sm font-normal leading-[22.4px] text-[#fa8c16] dark:text-[#ffa940]',
    },
    WAIT_PAY: {
      label: '待支付',
      className:
        'text-sm font-normal leading-[22.4px] text-[#fa8c16] dark:text-[#ffa940]',
    },
    WAIT_BUYER_PAY: {
      label: '等待买家付款',
      className:
        'text-sm font-normal leading-[22.4px] text-[#fa8c16] dark:text-[#ffa940]',
    },
    EXPIRED: {
      label: '已过期',
      className:
        'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]',
    },
    FAILED: {
      label: '支付失败',
      className:
        'text-sm font-medium leading-[22.4px] text-[#ff4d4f] dark:text-[#ff7875]',
    },
    CLOSED: {
      label: '已关闭',
      className:
        'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]',
    },
    REFUNDED: {
      label: '已退款',
      className:
        'text-sm font-medium leading-[22.4px] text-[#722ed1] dark:text-[#9254de]',
    },
    PARTIAL_REFUNDED: {
      label: '部分退款',
      className:
        'text-sm font-normal leading-[22.4px] text-[#9254de] dark:text-[#b37feb]',
    },
    CANCELLED: {
      label: '已取消',
      className:
        'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]',
    },
    CANCELED: {
      label: '已取消',
      className:
        'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]',
    },
  }

  const hit = map[k]
  if (hit)
    return hit

  return {
    label: raw,
    className:
      'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]',
  }
}

function mapOrderRecord(r: PaymentOrderRecord, index: number): OrderRow {
  const biz = String(r.bizorderno ?? r.orderNo ?? `order-${index}`)
  const pts = Number(r.pointsAmount ?? r.points ?? r.payPoints ?? 0)
  /** 后端 realAmount 为积分个数，与 pointsAmount 同单位；100 积分 = 1 元 */
  const rawCash = r.realAmount != null ? Number(r.realAmount) : pts
  const cashPoints = Number.isFinite(rawCash) ? rawCash : pts
  const amountYuan = cashPoints / POINTS_PER_CNY
  const createdAt = String(
    r.createdAt ?? r.gmtCreate ?? r.createTime ?? r.payTime ?? '',
  )
  const paidAt = String(r.paidAt ?? '')
  const subject = String(r.subject ?? '').trim() || '—'
  const channel = formatChannel(String(r.channel ?? ''))
  const paymentStatusRaw = String(r.paymentStatus ?? '').trim()
  const inv = String(r.invoiceStatus ?? r.invoiceApplyStatus ?? '')
  return {
    key: biz,
    orderId: biz,
    subject,
    channel,
    amountYuan,
    points: pts,
    createdAt: createdAt || '—',
    paidAt: paidAt || '—',
    paymentStatusRaw,
    action: mapInvoiceToAction(inv),
  }
}

const dateRange = ref<[Dayjs, Dayjs] | null>(null)
const orders = ref<OrderRow[]>([])
const orderTotal = ref(0)
const orderPageNo = ref(1)
const orderPageSize = ref(10)
const orderLoading = ref(false)

const ORDER_PICKER_POPUP_STYLE = { zIndex: 1200 } as const

function orderPickerGetPopupContainer(node: HTMLElement): HTMLElement {
  const wrap = node.closest('.ant-modal-wrap')
  return wrap instanceof HTMLElement ? wrap : document.body
}

async function fetchOrders() {
  orderLoading.value = true
  try {
    const params: {
      pageNo: number
      pageSize: number
      startDate?: string
      endDate?: string
    } = { pageNo: orderPageNo.value, pageSize: orderPageSize.value }
    if (dateRange.value) {
      params.startDate = dateRange.value[0].format('YYYY-MM-DD')
      params.endDate = dateRange.value[1].format('YYYY-MM-DD')
    }
    const data = await getPaymentOrders(params)
    const records = data?.records ?? []
    orders.value = records.map((r, i) => mapOrderRecord(r, i))
    orderTotal.value = data?.total ?? records.length
  }
  finally {
    orderLoading.value = false
  }
}

watch(dateRange, () => {
  orderPageNo.value = 1
})

watch([dateRange, orderPageNo, orderPageSize], () => {
  fetchOrders()
}, { immediate: true })

function formatAmount(yuan: number) {
  return `¥${yuan.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const invoiceModalOpen = ref(false)
const invoiceBizorderno = ref('')

function openInvoiceModal(record: OrderRow) {
  invoiceBizorderno.value = record.orderId
  invoiceModalOpen.value = true
}

function renderActionCell(record: OrderRow) {
  const { action } = record
  if (action === 'apply') {
    return h(
      'button',
      {
        type: 'button',
        class:
          'border-0 bg-transparent p-0 text-sm font-semibold leading-[22.4px] text-[#726FFF] hover:opacity-80',
        onClick: () => openInvoiceModal(record),
      },
      '申请开票',
    )
  }
  if (action === 'invoicing') {
    return h(
      'span',
      { class: 'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.65)]' },
      '开票中',
    )
  }
  if (action === 'applied_proxy') {
    return h('span', { class: 'inline-flex items-center gap-2' }, [
      h(
        'span',
        { class: 'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.25)]' },
        '已申请',
      ),
      h(
        'span',
        {
          class:
            'inline-flex h-[22px] items-center rounded-md bg-[rgba(215,215,255,0.40)] px-2.5 py-0.5 text-xs font-semibold leading-[18px] text-[#726FFF]',
        },
        '代开',
      ),
    ])
  }
  return h(
    'span',
    { class: 'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.25)]' },
    '已申请',
  )
}

function renderPaymentStatusCell(raw: string) {
  const { label, className } = getPaymentStatusDisplay(raw)
  return h('span', { class: className }, label)
}

const columns = computed<ColumnsType<OrderRow>>(() => [
  {
    title: '订单号',
    dataIndex: 'orderId',
    key: 'orderId',
    width: 200,
    ellipsis: true,
  },
  {
    title: '商品',
    dataIndex: 'subject',
    key: 'subject',
    width: 160,
    ellipsis: true,
  },
  {
    title: '支付渠道',
    dataIndex: 'channel',
    key: 'channel',
    width: 112,
    ellipsis: true,
  },
  {
    title: '实付金额',
    dataIndex: 'amountYuan',
    key: 'amount',
    width: 104,
    customRender: ({ record }) =>
      h(
        'span',
        { class: 'text-[13px] font-normal leading-[20.8px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]' },
        formatAmount(record.amountYuan),
      ),
  },
  {
    title: '积分',
    dataIndex: 'points',
    key: 'points',
    width: 88,
    customRender: ({ text }) =>
      h(
        'span',
        { class: 'text-sm font-normal leading-[22.4px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]' },
        Number(text).toLocaleString(),
      ),
  },
  {
    title: '下单时间',
    dataIndex: 'createdAt',
    key: 'createdAt',
    width: 168,
    ellipsis: true,
  },
  {
    title: '支付时间',
    dataIndex: 'paidAt',
    key: 'paidAt',
    width: 168,
    ellipsis: true,
  },
  {
    title: '支付状态',
    dataIndex: 'paymentStatusRaw',
    key: 'paymentStatusRaw',
    width: 120,
    customRender: ({ record }) => renderPaymentStatusCell(record.paymentStatusRaw),
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    fixed: 'right' as const,
    customRender: ({ record }) => renderActionCell(record),
  },
])

const ORDER_TABLE_ROW_PX = 48

const orderTableFrameRef = ref<HTMLElement | null>(null)
const orderTableBodyScrollY = ref(360)

function measureOrderTableBodyScroll() {
  const root = orderTableFrameRef.value
  if (!root)
    return
  const thead = root.querySelector('.ant-table-thead')
  const headH = thead instanceof HTMLElement ? thead.offsetHeight : 46
  orderTableBodyScrollY.value = Math.max(80, Math.floor(root.clientHeight - headH))
}

useResizeObserver(orderTableFrameRef, () => {
  void nextTick(() => measureOrderTableBodyScroll())
})

watch([orders, orderLoading], () => {
  void nextTick(() => measureOrderTableBodyScroll())
})

onMounted(() => {
  void nextTick(() => measureOrderTableBodyScroll())
})

const ORDER_TABLE_MIN_WIDTH = 1344

const orderTableScroll = computed(() => {
  const n = orders.value.length
  const maxY = orderTableBodyScrollY.value
  const contentH = n * ORDER_TABLE_ROW_PX
  const needY = n > 0 && contentH > maxY
  return {
    x: ORDER_TABLE_MIN_WIDTH,
    ...(needY ? { y: maxY } : {}),
  } as const
})

</script>

<template>
  <div
    class="flex min-h-0 min-w-0 flex-1 flex-col gap-4 self-stretch overflow-hidden"
  >
    <!-- 说明 -->
    <div
      class="shrink-0 rounded-xl bg-[rgba(215,215,255,0.40)] px-3 py-3 dark:bg-[rgba(215,215,255,0.12)]"
    >
      <p class="m-0 text-[13px] leading-[20.8px] text-[#726FFF]">
        注：您在该空间的充值记录，空间管理员亦可查看并进行统一财务管理。
      </p>
    </div>

    <!-- 充值订单：外框撑满剩余高度，表格在框内滚动 -->
    <div
      class="order-manage-section flex min-h-0 min-w-0 flex-1 flex-col gap-4 self-stretch overflow-hidden rounded-2xl border border-solid border-[rgba(0,0,0,0.10)] bg-white px-6 pb-6 pt-6 dark:border-[rgba(255,255,255,0.14)] dark:bg-[#1a1a1a]"
    >
      <div class="flex shrink-0 items-start justify-between gap-4 self-stretch">
        <span
          class="text-base font-semibold leading-[25.6px] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]"
        >
          充值订单
        </span>
        <a-range-picker
          v-model:value="dateRange"
          :bordered="false"
          class="order-range-picker h-8 w-[240px] shrink-0 rounded-md"
          :placeholder="['开始日期', '结束日期']"
          :get-popup-container="orderPickerGetPopupContainer"
          :popup-style="ORDER_PICKER_POPUP_STYLE"
        >
          <template #suffixIcon>
            <CalendarOutlined class="text-[rgba(0,0,0,0.25)]" />
          </template>
        </a-range-picker>
      </div>

      <div
        ref="orderTableFrameRef"
        class="order-table-frame order-table-wrap box-border min-h-0 w-full min-w-0 flex-1 overflow-hidden"
      >
        <a-spin :spinning="orderLoading" class="h-full min-h-0 w-full [&_.ant-spin-container]:h-full">
          <Table
            row-key="key"
            :columns="columns"
            :data-source="orders"
            :pagination="false"
            :scroll="orderTableScroll"
            size="small"
            class="order-manage-table"
          />
        </a-spin>
      </div>

      <div v-if="orderTotal > 0" class="flex shrink-0 justify-end pt-1">
        <a-pagination
          v-model:current="orderPageNo"
          v-model:page-size="orderPageSize"
          :total="orderTotal"
          :show-size-changer="true"
          size="small"
        />
      </div>
    </div>

    <InvoiceApplyModal v-model:open="invoiceModalOpen" :bizorderno="invoiceBizorderno" />
  </div>
</template>

<style scoped lang="scss">
.order-range-picker {
  background: #f3f3f7 !important;
  border: 1px solid #f0f0f0 !important;
  border-radius: 6px !important;

  :deep(.ant-picker) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding-inline: 11px !important;
  }

  :deep(.ant-picker-input > input) {
    font-size: 14px !important;
    color: rgba(0, 0, 0, 0.25) !important;
  }

  :deep(.ant-picker-input input::placeholder) {
    color: rgba(0, 0, 0, 0.25) !important;
  }
}

.order-manage-section {
  box-sizing: border-box;
  flex: 1 1 0;
  min-height: 0;
}

.order-table-wrap {
  display: flex;
  flex-direction: column;
}

.order-table-frame {
  flex: 1 1 0;
  min-height: 0;
}

.order-manage-table {
  flex: 1;
  min-height: 0;

  &:deep(.ant-table) {
    background: transparent;
  }

  &:deep(.ant-spin-nested-loading),
  &:deep(.ant-spin-container),
  &:deep(.ant-table-wrapper) {
    height: 100%;
  }

  &:deep(.ant-table-container) {
    border-radius: 8px;
    overflow: hidden;
    border: none;
  }

  &:deep(.ant-table.ant-table-small .ant-table-thead > tr > th) {
    background: #f3f3f7;
    color: rgba(0, 0, 0, 0.65);
    font-size: 12px;
    font-weight: 600;
    line-height: 19.2px;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    border-bottom: none;
    padding: 11px 16px;
  }

  &:deep(.ant-table.ant-table-small .ant-table-thead > tr > th:first-child) {
    padding-left: 20px;
    padding-right: 20px;
  }

  &:deep(.ant-table.ant-table-small .ant-table-tbody > tr > td) {
    padding: 16px;
    font-size: 14px;
    line-height: 22.4px;
    color: rgba(0, 0, 0, 0.65);
    border-bottom: 1px solid #f9f4ef;
  }

  &:deep(.ant-table.ant-table-small .ant-table-tbody > tr:last-child > td) {
    border-bottom: none;
  }
}
</style>
