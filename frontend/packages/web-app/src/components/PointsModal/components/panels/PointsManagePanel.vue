<script setup lang="ts">
import { AlipayCircleFilled } from '@ant-design/icons-vue'
import { message, Modal } from 'ant-design-vue'
import { computed, onMounted, onUnmounted, ref } from 'vue'

import type { PointsBalance } from '@/api/points'
import {
  getPaymentOrderStatus,
  getPaymentProducts,
  getPointsBalance,
  POINTS_PER_CNY,
  postPaymentRecharge,
} from '@/api/points'

/** 充值档位：来自 getPaymentProducts 的 products，price 为积分数量 */
interface RechargePackageOption {
  id: string
  points: number
  prodId: number
  versionId: number
}

const props = withDefaults(
  defineProps<{
    workspaceName?: string
  }>(),
  {
    workspaceName: '星辰科技工作空间',
  },
)

const balance = ref<PointsBalance | null>(null)
const balanceLoading = ref(false)
const packageOptions = ref<RechargePackageOption[]>([])
const productsLoading = ref(false)
const rechargeLoading = ref(false)

const rechargeQrOpen = ref(false)
const rechargeQrUrl = ref('')
/** 当前扫码支付订单号，用于轮询 GET /payment/order/status */
const rechargeBizorderno = ref('')
const paymentPollTimer = ref<ReturnType<typeof setTimeout> | null>(null)

/** 轮询间隔 5s，总时长超过则超时（3 分钟） */
const PAYMENT_POLL_INTERVAL_MS = 5000
const PAYMENT_POLL_TIMEOUT_MS = 3 * 60 * 1000

function stopPaymentStatusPolling() {
  if (paymentPollTimer.value != null) {
    clearTimeout(paymentPollTimer.value)
    paymentPollTimer.value = null
  }
}

/**
 * 打开二维码后开始轮询订单支付状态；PAID 则关闭弹窗并刷新余额；
 * 满 3 分钟未成功则提示超时并停止；订单不存在（404000）则停止。
 */
function startPaymentStatusPolling() {
  stopPaymentStatusPolling()
  const biz = rechargeBizorderno.value.trim()
  if (!biz) {
    message.warning('未获取到订单号，无法自动确认支付结果')
    return
  }
  const startedAt = Date.now()

  const scheduleNext = () => {
    paymentPollTimer.value = setTimeout(() => {
      void pollOnce()
    }, PAYMENT_POLL_INTERVAL_MS)
  }

  const pollOnce = async () => {
    if (!rechargeQrOpen.value) {
      stopPaymentStatusPolling()
      return
    }
    if (Date.now() - startedAt > PAYMENT_POLL_TIMEOUT_MS) {
      stopPaymentStatusPolling()
      message.warning('等待支付结果超时，请稍后在订单管理中确认，或重新发起充值')
      return
    }
    try {
      const data = await getPaymentOrderStatus(biz)
      if (data?.paymentStatus === 'PAID') {
        stopPaymentStatusPolling()
        rechargeQrOpen.value = false
        rechargeQrUrl.value = ''
        rechargeBizorderno.value = ''
        message.success('支付成功')
        await loadBalance()
        return
      }
    }
    catch (e: unknown) {
      const code = typeof e === 'object' && e !== null && 'code' in e
        ? String((e as { code?: string }).code)
        : ''
      if (code === '404000') {
        stopPaymentStatusPolling()
        message.warning('订单不存在或已失效')
        return
      }
    }
    scheduleNext()
  }

  void pollOnce()
}

function isChargeQrUrl(pay: unknown): pay is string {
  return typeof pay === 'string' && /^https?:\/\//i.test(pay.trim())
}

function onRechargeQrClose() {
  stopPaymentStatusPolling()
  rechargeQrOpen.value = false
  rechargeQrUrl.value = ''
  rechargeBizorderno.value = ''
  message.warning('充值失败')
  void loadBalance()
}

const POINTS_PER_YUAN = POINTS_PER_CNY
const CUSTOM_POINTS_MIN = 100
const CUSTOM_POINTS_MAX = 99_999_999

const selectedPackageId = ref<string>('')
const customPoints = ref('')

const selectedPackage = computed((): RechargePackageOption | null => {
  const list = packageOptions.value
  if (list.length === 0)
    return null
  const cur = list.find(p => p.id === selectedPackageId.value)
  if (cur)
    return cur
  return list.length > 1 ? list[1]! : list[0]!
})

/** 自定义框有内容时视为走自定义档位，套餐仅保留高亮逻辑上的「未选中」 */
const isCustomMode = computed(() => customPoints.value.length > 0)

/** 仅数字；去掉前导 0；限制上限位数 */
function onCustomPointsInput(e: Event) {
  const el = e.target as HTMLInputElement
  let v = el.value.replace(/\D/g, '')
  v = v.replace(/^0+(?=\d)/, '')
  if (v.length > String(CUSTOM_POINTS_MAX).length)
    v = v.slice(0, String(CUSTOM_POINTS_MAX).length)
  if (v && Number(v) > CUSTOM_POINTS_MAX)
    v = String(CUSTOM_POINTS_MAX)
  customPoints.value = v
  if (el.value !== v)
    el.value = v
}

const parsedCustomPoints = computed(() => {
  const s = customPoints.value
  if (!s)
    return null
  const n = Number(s)
  if (!Number.isFinite(n) || n < 1)
    return null
  return Math.min(n, CUSTOM_POINTS_MAX)
})

/** 实际充值积分：有合法自定义用自定义，否则用当前选中套餐 */
const effectiveRechargePoints = computed(() =>
  parsedCustomPoints.value ?? selectedPackage.value?.points ?? 0,
)

const formattedRechargeCash = computed(() =>
  formatCashFromPoints(effectiveRechargePoints.value),
)

/** 套餐档位：正整数且不超过上限；自定义（若启用）需满足 100 倍数与区间 */
const canRecharge = computed(() => {
  if (!selectedPackage.value)
    return false
  const custom = parsedCustomPoints.value
  if (custom != null) {
    return custom >= CUSTOM_POINTS_MIN && custom <= CUSTOM_POINTS_MAX && custom % 100 === 0
  }
  const p = selectedPackage.value.points
  return p > 0 && p <= CUSTOM_POINTS_MAX
})

function formatCashFromPoints(points: number) {
  const yuan = points / POINTS_PER_YUAN
  return `¥${yuan.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function selectPackage(id: string) {
  selectedPackageId.value = id
  customPoints.value = ''
}

const currentBalance = computed(() => balance.value?.totalBalance ?? 0)
const monthConsumed = computed(() => balance.value?.monthConsumption ?? 0)
const spaceTotal = computed(() => balance.value?.tenantTotalBalance ?? 0)
const balanceCap = computed(() => {
  const cap = spaceTotal.value
  return cap > 0 ? cap : Math.max(currentBalance.value, 1)
})
const quotaPercent = computed(() => {
  const q = balance.value?.freeQuota
  if (!q?.weeklyTotal)
    return 0
  return Math.min(100, Math.round((q.weeklyUsed / q.weeklyTotal) * 100))
})

const balanceUsagePercent = computed(() => {
  const cap = balanceCap.value
  if (!cap || cap <= 0)
    return 0
  return Math.min(100, Math.max(0, (currentBalance.value / cap) * 100))
})

const balanceProgressBarColor = computed(() => {
  const p = balanceUsagePercent.value
  if (p < 20)
    return '#F14439'
  if (p < 40)
    return '#F79007'
  return '#726FFF'
})

async function loadBalance() {
  balanceLoading.value = true
  try {
    balance.value = await getPointsBalance()
  }
  finally {
    balanceLoading.value = false
  }
}

function parseRechargePackages(raw: unknown): RechargePackageOption[] {
  if (raw == null)
    return []
  const list: unknown = Array.isArray(raw)
    ? raw
    : (raw as Record<string, unknown>).products
      ?? (raw as Record<string, unknown>).records
      ?? (raw as Record<string, unknown>).list
  if (!Array.isArray(list))
    return []
  const out: RechargePackageOption[] = []
  for (const item of list) {
    if (item == null || typeof item !== 'object')
      continue
    const p = item as Record<string, unknown>
    const prodId = p.id ?? p.prodId ?? p.prod_id
    const versionRaw = p.versionid ?? p.versionId ?? p.version_id
    const priceRaw = p.price ?? p.floorprice ?? p.floorPrice
    const versionId = typeof versionRaw === 'number' ? versionRaw : Number(versionRaw)
    const points = typeof priceRaw === 'number' ? priceRaw : Number(priceRaw)
    if (typeof prodId !== 'number' || !Number.isFinite(versionId) || !Number.isFinite(points) || points <= 0)
      continue
    out.push({
      id: String(prodId),
      points,
      prodId,
      versionId,
    })
  }
  out.sort((a, b) => a.points - b.points)
  return out
}

async function loadPaymentProducts() {
  productsLoading.value = true
  try {
    const raw = await getPaymentProducts({ pageNo: 1, pageSize: 20 })
    const opts = parseRechargePackages(raw)
    packageOptions.value = opts
    if (opts.length === 0) {
      selectedPackageId.value = ''
      return
    }
    const preferSecond = opts.length > 1 ? opts[1]! : opts[0]!
    selectedPackageId.value = preferSecond.id
  }
  catch {
    packageOptions.value = []
    selectedPackageId.value = ''
  }
  finally {
    productsLoading.value = false
  }
}

onMounted(async () => {
  await loadBalance()
  await loadPaymentProducts()
})

onUnmounted(() => {
  stopPaymentStatusPolling()
})

async function handleRecharge() {
  const pkg = selectedPackage.value
  if (!pkg) {
    message.warning('暂无可购商品，请稍后再试')
    return
  }
  const custom = parsedCustomPoints.value
  if (custom != null && (custom < CUSTOM_POINTS_MIN || custom > CUSTOM_POINTS_MAX || custom % 100 !== 0)) {
    message.warning(`自定义积分需为 ${CUSTOM_POINTS_MIN}～${CUSTOM_POINTS_MAX.toLocaleString()} 且为 100 的倍数`)
    return
  }
  rechargeLoading.value = true
  try {
    const res = await postPaymentRecharge({
      prodId: pkg.prodId,
      versionId: pkg.versionId,
      channel: 'alipay_qr',
      ...(custom != null ? { customPoints: custom } : {}),
    })
    const pay = res?.charge
    if (isChargeQrUrl(pay)) {
      rechargeQrUrl.value = pay.trim()
      rechargeBizorderno.value = String(res?.bizorderno ?? '').trim()
      rechargeQrOpen.value = true
      startPaymentStatusPolling()
      return
    }
    message.success('订单已创建')
    await loadBalance()
  }
  finally {
    rechargeLoading.value = false
  }
}
</script>

<template>
  <div
    class="flex min-h-0 min-w-0 flex-1 flex-col self-stretch overflow-hidden"
  >
    <div
      class="flex min-h-0 min-w-0 flex-1 flex-col gap-6 overflow-y-auto overscroll-contain px-6 pb-6"
    >
    <div class="text-[15px] leading-[25.5px] !text-[rgba(0,0,0,0.65)] dark:!text-[rgba(255,255,255,0.65)]">
      <span>充值后可使用星辰RPA平台提供的AI智能、OCR、验证码等扩展服务。</span>
      <button
        type="button"
        class="ml-1 border-0 bg-transparent p-0 text-[15px] font-normal leading-[25.5px] text-[#726FFF] hover:opacity-80"
      >
        查看计费项规则
      </button>
    </div>

    <div class="flex flex-col gap-6 self-stretch">
      <a-spin :spinning="balanceLoading" class="w-full [&_.ant-spin-container]:min-h-[144px]">
        <div class="grid w-full grid-cols-2 gap-4 self-stretch">
        <!-- 当前余额 -->
        <div
          class="flex min-h-[144px] min-w-0 flex-col gap-[14px] rounded-2xl border border-solid bg-white p-6 !border-[rgba(0,0,0,0.10)] dark:bg-[#1a1a1a] dark:!border-[rgba(255,255,255,0.14)]"
        >
          <div class="relative h-5 w-full shrink-0">
            <span
              class="absolute left-0 top-0 text-sm font-normal leading-[22px] !text-[rgba(0,0,0,0.65)] dark:!text-[rgba(255,255,255,0.65)]"
            >
              当前余额
            </span>
            <div
              class="absolute right-0 top-[-1px] inline-flex items-center justify-start gap-1"
            >
              <span
                class="text-xs font-normal leading-[22px] !text-[rgba(0,0,0,0.65)] dark:!text-[rgba(255,255,255,0.65)]"
              >
                空间总额 {{ spaceTotal.toLocaleString() }}
              </span>
              <!-- <div
                class="flex h-[22px] items-center justify-center gap-2.5 rounded-md bg-[rgba(215,215,255,0.40)] px-2.5 py-0.5 dark:bg-[rgba(215,215,255,0.15)]"
              >
                <span class="text-xs font-semibold leading-[18px] text-[#726FFF]">
                  配额{{ quotaPercent }}%
                </span>
              </div> -->
            </div>
          </div>
          <div class="inline-flex w-full items-end justify-start gap-2.5 self-stretch">
            <span
              class="font-sans text-[44px] font-bold leading-10 !text-[rgba(0,0,0,0.85)] dark:!text-[rgba(255,255,255,0.85)]"
            >
              {{ currentBalance.toLocaleString() }}
            </span>
            <span
              class="text-sm font-normal leading-[22px] !text-[rgba(0,0,0,0.45)] dark:!text-[rgba(255,255,255,0.45)]"
            >
              /{{ balanceCap.toLocaleString() }}积分
            </span>
          </div>
          <div class="h-2 w-full overflow-hidden rounded-full bg-[#ECEDF4] dark:bg-white/[0.08]">
            <div
              class="h-full min-w-0 rounded-full transition-[width,background-color] duration-300"
              :style="{ width: `${balanceUsagePercent}%`, backgroundColor: balanceProgressBarColor }"
            />
          </div>
        </div>

        <!-- 本月消耗 -->
        <div
          class="flex min-h-[144px] min-w-0 flex-col gap-[14px] rounded-2xl border border-solid bg-white p-6 !border-[rgba(0,0,0,0.10)] dark:bg-[#1a1a1a] dark:!border-[rgba(255,255,255,0.14)]"
        >
          <div class="relative h-5 w-full shrink-0">
            <span
              class="absolute left-0 top-0 text-sm font-normal leading-[22px] !text-[rgba(0,0,0,0.65)] dark:!text-[rgba(255,255,255,0.65)]"
            >
              本月消耗
            </span>
          </div>
          <div class="inline-flex w-full flex-1 items-end justify-start gap-2.5">
            <span
              class="font-sans text-[44px] font-bold leading-10 !text-[rgba(0,0,0,0.85)] dark:!text-[rgba(255,255,255,0.85)]"
            >
              {{ monthConsumed.toLocaleString() }}
            </span>
            <span
              class="text-sm font-normal leading-[22px] !text-[rgba(0,0,0,0.45)] dark:!text-[rgba(255,255,255,0.45)]"
            >
              积分
            </span>
          </div>
        </div>
        </div>
      </a-spin>

      <!-- 充值积分 -->
      <div class="flex flex-col gap-4 self-stretch">
        <div class="text-xl font-semibold leading-8 text-[#1A1512] dark:text-white">
          充值积分
        </div>

        <div
          class="inline-flex items-center justify-start gap-2.5 self-stretch rounded-xl bg-[rgba(215,215,255,0.40)] px-3 py-2.5 dark:bg-[rgba(215,215,255,0.12)]"
        >
          <p class="text-[13px] leading-[20.8px] text-[#726FFF]">
            <span class="font-normal">注：您正在为 </span>
            <span class="font-semibold">{{ workspaceName }}</span>
            <span class="font-normal"> 充值，充值后积分将由空间内成员共享使用。</span>
          </p>
        </div>

        <a-spin :spinning="productsLoading" class="min-h-[120px] w-full [&_.ant-spin-container]:flex [&_.ant-spin-container]:w-full [&_.ant-spin-container]:gap-4">
        <div class="flex w-full gap-[16px] self-stretch">
          <button
            v-for="pkg in packageOptions"
            :key="pkg.id"
            type="button"
            class="flex h-[120px] min-h-[120px] min-w-0 flex-1 flex-col items-center justify-center gap-1 rounded-2xl border border-solid bg-white transition-colors dark:bg-[#1a1a1a]"
            :class="
              !isCustomMode && selectedPackageId === pkg.id
                ? '!border-[#726FFF] bg-[rgba(215,215,255,0.40)] dark:bg-[rgba(215,215,255,0.12)]'
                : '!border-[rgba(0,0,0,0.10)] dark:!border-[rgba(255,255,255,0.14)]'
            "
            @click="selectPackage(pkg.id)"
          >
            <span class="text-center font-sans text-[32px] font-semibold text-[#1A1512] dark:text-white">
              {{ pkg.points.toLocaleString() }}
            </span>
            <span
              class="text-center font-sans text-sm font-normal leading-[22px] !text-[rgba(0,0,0,0.65)] dark:!text-[rgba(255,255,255,0.65)]"
            >
              {{ formatCashFromPoints(pkg.points) }}
            </span>
          </button>
        </div>
        </a-spin>

        <!-- <div
          class="inline-flex h-10 min-w-0 items-center gap-2 self-stretch rounded-xl border border-solid bg-white px-3 !border-[rgba(0,0,0,0.10)] dark:bg-[#1a1a1a] dark:!border-[rgba(255,255,255,0.14)]"
        >
          <input
            :value="customPoints"
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            autocomplete="off"
            placeholder="请输入自定义积分（100-99,999,999）"
            class="min-w-0 flex-1 border-0 bg-white p-0 text-[15px] font-normal !text-[rgba(0,0,0,0.85)] outline-none ring-0 placeholder:!text-[rgba(0,0,0,0.25)] focus:ring-0 dark:bg-[#1a1a1a] dark:!text-[rgba(255,255,255,0.85)] dark:placeholder:!text-[rgba(255,255,255,0.25)]"
            @input="onCustomPointsInput"
          >
          <span
            class="shrink-0 text-sm font-normal leading-[22.4px] !text-[rgba(0,0,0,0.25)] dark:!text-[rgba(255,255,255,0.25)]"
          >
            积分
          </span>
        </div> -->
      </div>
    </div>
    </div>

    <!-- 贴弹窗内容区最底、全宽，不受上方 px-6 影响；顶部分割线 -->
    <div
      class="points-manage-footer-bar box-border flex h-[88px] w-full shrink-0 flex-col justify-center border-t border-solid border-[rgba(0,0,0,0.06)] bg-white dark:border-[rgba(255,255,255,0.08)] dark:bg-[#141414]"
    >
      <div class="flex h-full min-h-0 items-center justify-between gap-4 px-6">
        <div class="inline-flex min-w-0 flex-1 flex-col items-start justify-center gap-1">
          <div>
            <span
              class="font-sans text-2xl font-semibold !text-[rgba(0,0,0,0.85)] dark:!text-[rgba(255,255,255,0.85)]"
            >
              {{ formattedRechargeCash }}
            </span>
          </div>
          <div class="text-center">
            <span
              class="text-xs font-normal !text-[rgba(0,0,0,0.65)] dark:!text-[rgba(255,255,255,0.65)]"
            >
              充值即表示您同意《
            </span>
            <button
              type="button"
              class="border-0 bg-transparent p-0 text-xs font-normal text-[#726FFF] underline"
            >
              星辰RPA积分充值购买协议
            </button>
            <span
              class="text-xs font-normal !text-[rgba(0,0,0,0.65)] dark:!text-[rgba(255,255,255,0.65)]"
            >
              》
            </span>
          </div>
        </div>
        <button
          type="button"
          class="flex h-[46px] w-[140px] shrink-0 items-center justify-center rounded-[10px] border-0 bg-[#726FFF] px-8 hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="!canRecharge || rechargeLoading || productsLoading"
          :aria-busy="rechargeLoading"
          @click="handleRecharge"
        >
          <span class="text-center text-[15px] font-semibold text-white">
            {{ rechargeLoading ? '提交中…' : '立即充值' }}
          </span>
        </button>
      </div>
    </div>
  </div>

  <Modal
    :open="rechargeQrOpen"
    :width="360"
    :z-index="1200"
    :footer="null"
    centered
    destroy-on-close
    wrap-class-name="points-recharge-qr-modal-wrap"
    class="points-recharge-qr-modal"
    @cancel="onRechargeQrClose"
  >
    <template #title>
      <div class="inline-flex items-center gap-2">
        <AlipayCircleFilled class="text-[22px] text-[#1677FF]" />
        <span class="text-base font-semibold text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]">
          支付宝扫码支付
        </span>
      </div>
    </template>
    <div class="flex flex-col items-center px-2 pb-2 pt-1">
      <div
        class="flex h-[220px] w-[220px] items-center justify-center overflow-hidden rounded-lg border border-solid border-[rgba(0,0,0,0.06)] bg-white dark:border-[rgba(255,255,255,0.12)] dark:bg-[#1a1a1a]"
      >
        <img
          v-if="rechargeQrUrl"
          :src="rechargeQrUrl"
          alt="支付宝收款二维码"
          class="max-h-full max-w-full object-contain"
        >
      </div>
      <p class="mt-4 text-center text-sm leading-[22px] !text-[rgba(0,0,0,0.45)] dark:!text-[rgba(255,255,255,0.45)]">
        请使用支付宝扫描上方二维码完成支付
      </p>
      <p class="mt-1 text-center text-xs leading-5 !text-[rgba(0,0,0,0.35)] dark:!text-[rgba(255,255,255,0.35)]">
        支付成功后将自动关闭本窗口并更新余额（最长等待约 3 分钟）
      </p>
    </div>
  </Modal>
</template>
