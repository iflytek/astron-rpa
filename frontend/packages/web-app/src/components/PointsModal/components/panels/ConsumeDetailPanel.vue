<script setup lang="ts">
import { CalendarOutlined, DownOutlined } from '@ant-design/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from 'echarts/components'
import type { EChartsCoreOption } from 'echarts/core'
import type { Dayjs } from 'dayjs'
import dayjs from 'dayjs'
import type { ColumnsType } from 'ant-design-vue/es/table'
import { Table } from 'ant-design-vue'
import { useResizeObserver } from '@vueuse/core'
import { computed, h, nextTick, onMounted, ref, watch } from 'vue'
import VChart from 'vue-echarts'

import type {
  PointsConsumptionBarData,
  PointsConsumptionParams,
  PointsConsumptionPieData,
  PointsConsumptionRecord,
} from '@/api/points'
import {
  getPointsConsumptionBar,
  getPointsConsumptionPie,
  getPointsConsumptions,
} from '@/api/points'

use([CanvasRenderer, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent])

type ChartScope = 'today' | 'month'

const PIE_COLORS = ['#5D59FF', '#7A76F5', '#9B97FA', '#BEBCFD', '#E4E3FA'] as const

interface ConsumeRow {
  key: string
  time: string
  module: string
  provider: string
  points: number
  /** 0 积分 + 「免费积分」标签 */
  freeTag?: boolean
  /** 展示为「n（免费额度）」 */
  freeQuota?: boolean
}

const MODULE_OPTIONS = [
  { value: 'all', label: '全部' },
  { value: 'AI大模型', label: 'AI大模型' },
  { value: '智能组件', label: '智能组件' },
  { value: 'OCR识别', label: 'OCR识别' },
  { value: '语音识别', label: '语音识别' },
  { value: '验证码识别', label: '验证码识别' },
] as const

/** 与筛选项一致的中文名；已是中文则不再翻译 */
const KNOWN_CN_MODULES = new Set(
  MODULE_OPTIONS.filter(o => o.value !== 'all').map(o => o.label),
)

/** 后端 module 枚举（英文/下划线等）→ 中文展示，与 MODULE_OPTIONS 对齐 */
const MODULE_CODE_TO_CN: Record<string, string> = {
  AI: 'AI大模型',
  LLM: 'AI大模型',
  AI_LLM: 'AI大模型',
  AI_MODEL: 'AI大模型',
  LARGE_LANGUAGE_MODEL: 'AI大模型',
  SMART_COMPONENT: '智能组件',
  SMART_COMP: '智能组件',
  INTELLIGENT_COMPONENT: '智能组件',
  OCR: 'OCR识别',
  OCR_RECOGNITION: 'OCR识别',
  ASR: '语音识别',
  SPEECH: '语音识别',
  SPEECH_RECOGNITION: '语音识别',
  VOICE: '语音识别',
  VOICE_RECOGNITION: '语音识别',
  CAPTCHA: '验证码识别',
  CAPTCHA_RECOGNITION: '验证码识别',
  VERIFICATION: '验证码识别',
  VERIFICATION_CODE: '验证码识别',
}

function normalizeModuleCode(raw: string): string {
  return raw
    .trim()
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .toUpperCase()
}

/** 消耗明细 / 饼图：module 字段展示为中文 */
function formatConsumptionModule(raw: string): string {
  const s = raw.trim()
  if (!s)
    return '—'
  if (KNOWN_CN_MODULES.has(s))
    return s

  const code = normalizeModuleCode(s)
  if (MODULE_CODE_TO_CN[code])
    return MODULE_CODE_TO_CN[code]

  const upper = s.toUpperCase()
  if (MODULE_CODE_TO_CN[upper])
    return MODULE_CODE_TO_CN[upper]

  return s
}

const MODULE_FILTER_PREFIX = '消耗模块：'

/** 收起时 Select 用完整 label；下拉项用 #option 只展示短名 */
const moduleFilterSelectOptions = MODULE_OPTIONS.map(o => ({
  value: o.value,
  label: `${MODULE_FILTER_PREFIX}${o.label}`,
}))

function moduleFilterDropdownLabel(label: unknown): string {
  if (typeof label !== 'string')
    return String(label ?? '')
  return label.startsWith(MODULE_FILTER_PREFIX)
    ? label.slice(MODULE_FILTER_PREFIX.length)
    : label
}

const chartScope = ref<ChartScope>('today')
const moduleFilter = ref<string>('all')
const dateRange = ref<[Dayjs, Dayjs] | null>(null)

const chartLoading = ref(false)
/** 柱状图：服务端按桶返回 label + usedPoints */
const barChartData = ref<PointsConsumptionBarData | null>(null)
/** 饼图：按模块聚合 */
const pieChartData = ref<PointsConsumptionPieData | null>(null)

const tableRecords = ref<ConsumeRow[]>([])
const tableTotal = ref(0)
const tablePageNo = ref(1)
const tablePageSize = ref(20)
const tableLoading = ref(false)

function mapConsumptionRow(r: PointsConsumptionRecord): ConsumeRow {
  return {
    key: String(r.id),
    time: r.consumedAt,
    module: r.module,
    provider: r.provider,
    points: r.points,
    freeTag: r.isFree && r.points === 0,
    freeQuota: r.isFree && r.points > 0,
  }
}

async function loadChartData() {
  chartLoading.value = true
  const period = chartScope.value
  try {
    const [bar, pie] = await Promise.all([
      getPointsConsumptionBar({ period }, { toast: false }),
      getPointsConsumptionPie({ period }, { toast: false }),
    ])
    barChartData.value = bar
    pieChartData.value = pie
  }
  catch {
    barChartData.value = null
    pieChartData.value = null
  }
  finally {
    chartLoading.value = false
  }
}

async function loadTable() {
  tableLoading.value = true
  try {
    const params: PointsConsumptionParams = {
      pageNo: tablePageNo.value,
      pageSize: tablePageSize.value,
    }
    if (moduleFilter.value !== 'all')
      params.module = moduleFilter.value
    if (dateRange.value) {
      params.startDate = dateRange.value[0].format('YYYY-MM-DD')
      params.endDate = dateRange.value[1].format('YYYY-MM-DD')
    }
    const data = await getPointsConsumptions(params)
    tableRecords.value = data.records.map(mapConsumptionRow)
    tableTotal.value = data.total
  }
  finally {
    tableLoading.value = false
  }
}

watch(chartScope, () => {
  loadChartData()
})

watch([moduleFilter, dateRange], () => {
  tablePageNo.value = 1
})

watch([moduleFilter, dateRange, tablePageNo, tablePageSize], () => {
  loadTable()
}, { immediate: true })

const consumeTitle = computed(() => (chartScope.value === 'today' ? '今日消耗' : '本月消耗'))

const chartTotalPoints = computed(() => barChartData.value?.totalUsed ?? 0)

const pieSlices = computed(() => {
  const items = pieChartData.value?.items ?? []
  return items.map((it, i) => ({
    name: formatConsumptionModule(it.module),
    value: it.usedPoints,
    itemStyle: { color: PIE_COLORS[i % PIE_COLORS.length] },
  }))
})

const pieDistributionTitle = computed(() =>
  chartScope.value === 'today' ? '今日消耗分布' : '本月消耗分布',
)

/** 柱状默认浅蓝；hover 为品牌紫（与设计稿一致） */
const BAR_COLOR_DEFAULT = 'rgba(114, 111, 255, 0.2)'
const BAR_COLOR_HOVER = '#726FFF'

function formatBarTooltipHtml(timeRange: string, value: number): string {
  return [
    '<div style="display:flex;justify-content:space-between;align-items:center;gap:16px;',
    'min-width:140px;padding:8px 12px;background:#fff;border-radius:8px;',
    'box-shadow:0 2px 4px rgba(0,0,0,0.02),0 1px 6px -1px rgba(0,0,0,0.02),0 1px 2px rgba(0,0,0,0.03);',
    'border:1px solid rgba(0,0,0,0.04);font-family:PingFang SC,-apple-system,sans-serif;">',
    `<span style="color:rgba(0,0,0,0.65);font-size:12px;line-height:20px;">${timeRange}</span>`,
    `<span style="color:rgba(0,0,0,0.85);font-size:13px;font-weight:600;line-height:20px;">${value}</span>`,
    '</div>',
  ].join('')
}

function buildBarSeriesData(values: number[]) {
  return values.map(v => ({
    value: v,
    itemStyle: {
      color: BAR_COLOR_DEFAULT,
      borderRadius: [4, 4, 0, 0],
    },
    emphasis: {
      focus: 'self',
      itemStyle: {
        color: BAR_COLOR_HOVER,
        borderRadius: [4, 4, 0, 0],
      },
    },
  }))
}

const barChartOption = computed<EChartsCoreOption>(() => {
  const barSeriesCommon = {
    type: 'bar' as const,
    /** 无消耗时段保留极短占位条，时间轴不断档 */
    barMinHeight: 3,
    /** 类目间固定 2px 间隔，柱宽随容器自适应（不设 barMaxWidth） */
    barGap: '0%',
    barCategoryGap: 2,
    silent: false,
  }

  const items = barChartData.value?.items ?? []

  if (chartScope.value === 'today') {
    const values = items.map(i => i.usedPoints)
    const categories = items.map(i => i.label)
    const data = buildBarSeriesData(values)
    return {
      grid: { left: 2, right: 2, top: 4, bottom: 18, containLabel: false },
      xAxis: {
        type: 'category',
        data: categories,
        boundaryGap: [0.008, 0.008],
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: 'rgba(0,0,0,0.45)',
          fontSize: 10,
          lineHeight: 16,
          interval: 0,
          formatter: (val: string) => {
            const h = Number.parseInt(String(val).split(':')[0] ?? '0', 10)
            return Number.isFinite(h) && [0, 6, 12, 18].includes(h) ? val : ''
          },
        },
      },
      yAxis: {
        type: 'value',
        show: false,
        scale: true,
        boundaryGap: [0, 0.12],
      },
      tooltip: {
        /** item 触发才能让 emphasis 着色为 hover 蓝，与设计稿一致 */
        trigger: 'item',
        backgroundColor: 'transparent',
        borderWidth: 0,
        padding: 0,
        extraCssText: 'box-shadow:none;',
        formatter: (params: unknown) => {
          const p = params as { dataIndex?: number }
          if (p == null || typeof p.dataIndex !== 'number')
            return ''
          const idx = p.dataIndex
          const v = values[idx] ?? 0
          const cur = items[idx]
          const next = items[idx + 1]
          const range
            = cur && next
              ? `${cur.label}-${next.label}`
              : cur
                ? `${cur.label}-24:00`
                : ''
          return formatBarTooltipHtml(range, v)
        },
      },
      series: [{ ...barSeriesCommon, data }],
    }
  }

  const monthVals = items.map(i => i.usedPoints)
  const categories = items.map((it) => {
    const d = dayjs(it.label)
    return d.isValid() ? `${d.date()}日` : it.label
  })
  const data = buildBarSeriesData(monthVals)
  const n = monthVals.length
  return {
    grid: { left: 2, right: 2, top: 4, bottom: 18, containLabel: false },
    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: [0.008, 0.008],
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: 'rgba(0,0,0,0.45)',
        fontSize: 10,
        interval: 0,
        formatter: (_value: string, index: number) => {
          const day = index + 1
          if (day === 1 || day === 15 || day === n || (n > 0 && day % 5 === 0))
            return `${day}日`
          return ''
        },
      },
    },
    yAxis: {
      type: 'value',
      show: false,
      scale: true,
      boundaryGap: [0, 0.1],
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'transparent',
      borderWidth: 0,
      padding: 0,
      extraCssText: 'box-shadow:none;',
      formatter: (params: unknown) => {
        const p = params as { dataIndex?: number }
        if (p == null || typeof p.dataIndex !== 'number')
          return ''
        const idx = p.dataIndex
        const v = monthVals[idx] ?? 0
        const rawLabel = items[idx]?.label ?? ''
        return formatBarTooltipHtml(rawLabel, v)
      },
    },
    series: [{ ...barSeriesCommon, data }],
  }
})

const pieChartOption = computed<EChartsCoreOption>(() => {
  const slices = pieSlices.value
  const pieTotal = slices.reduce((s, p) => s + p.value, 0)
  function formatPieTooltip(params: unknown): string {
    const p = params as { name?: string; value?: number; color?: string; percent?: number }
    if (!p?.name)
      return ''
    const pct
      = typeof p.percent === 'number'
        ? p.percent.toFixed(1)
        : pieTotal > 0 && typeof p.value === 'number'
          ? ((p.value / pieTotal) * 100).toFixed(1)
          : '0'
    const color = p.color ?? '#726FFF'
    return [
      '<div style="display:flex;align-items:center;gap:10px;padding:10px 14px;',
      'background:#fff;border-radius:12px;',
      'box-shadow:0 2px 8px rgba(0,0,0,0.06),0 1px 3px rgba(0,0,0,0.04);',
      'font-family:PingFang SC,-apple-system,sans-serif;min-width:168px;">',
      `<span style="display:inline-block;width:4px;height:14px;border-radius:999px;background:${color};flex-shrink:0;"></span>`,
      `<span style="color:rgba(0,0,0,0.65);font-size:13px;line-height:20px;">${p.name}</span>`,
      `<span style="margin-left:auto;color:rgba(0,0,0,0.85);font-size:13px;font-weight:600;line-height:20px;">${pct}%</span>`,
      '</div>',
    ].join('')
  }
  return {
    tooltip: {
      trigger: 'item',
      show: true,
      backgroundColor: 'transparent',
      borderWidth: 0,
      padding: 0,
      shadowBlur: 0,
      extraCssText: 'box-shadow:none;',
      formatter: formatPieTooltip,
    },
    series: [
      {
        type: 'pie',
        radius: ['56%', '74%'],
        center: ['28%', '52%'],
        clockwise: true,
        minAngle: 2,
        avoidLabelOverlap: false,
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: { show: false },
        emphasis: {
          focus: 'self',
          scale: true,
          scaleSize: 6,
          itemStyle: {
            shadowBlur: 12,
            shadowColor: 'rgba(93, 89, 255, 0.25)',
          },
        },
        blur: {
          itemStyle: { opacity: 0.55 },
        },
        data: slices,
      },
    ],
    legend: {
      orient: 'vertical',
      right: '0%',
      top: 'middle',
      itemWidth: 8,
      itemHeight: 8,
      icon: 'circle',
      itemGap: 10,
      textStyle: {
        color: 'rgba(0,0,0,0.65)',
        fontSize: 12,
        fontFamily: 'PingFang SC, sans-serif',
        lineHeight: 16,
      },
    },
  }
})

const CONSUME_TABLE_ROW_PX = 48

const consumeTableFrameRef = ref<HTMLElement | null>(null)
const consumeTableBodyScrollY = ref(360)

function measureConsumeTableBodyScroll() {
  const root = consumeTableFrameRef.value
  if (!root)
    return
  const thead = root.querySelector('.ant-table-thead')
  const headH = thead instanceof HTMLElement ? thead.offsetHeight : 46
  consumeTableBodyScrollY.value = Math.max(80, Math.floor(root.clientHeight - headH))
}

useResizeObserver(consumeTableFrameRef, () => {
  void nextTick(() => measureConsumeTableBodyScroll())
})

watch([tableRecords, tableLoading], () => {
  void nextTick(() => measureConsumeTableBodyScroll())
})

onMounted(() => {
  loadChartData()
  void nextTick(() => measureConsumeTableBodyScroll())
})

const consumeTableScroll = computed(() => {
  const n = tableRecords.value.length
  if (n === 0)
    return undefined
  const maxY = consumeTableBodyScrollY.value
  const contentH = n * CONSUME_TABLE_ROW_PX
  if (contentH <= maxY)
    return undefined
  return { y: maxY } as const
})

/** 避免父级 overflow:hidden 裁切；zIndex 需高于积分弹窗 a-modal 的 1100 */
function consumePickerGetPopupContainer(node: HTMLElement): HTMLElement {
  const wrap = node.closest('.ant-modal-wrap')
  return wrap instanceof HTMLElement ? wrap : document.body
}

const CONSUME_PICKER_POPUP_STYLE = { zIndex: 1200 } as const

function consumeSelectGetPopupContainer(node: HTMLElement): HTMLElement {
  const wrap = node.closest('.ant-modal-wrap')
  return wrap instanceof HTMLElement ? wrap : document.body
}

const columns = computed<ColumnsType<ConsumeRow>>(() => [
  {
    title: '时间',
    dataIndex: 'time',
    key: 'time',
    ellipsis: true,
  },
  {
    title: '消耗模块',
    dataIndex: 'module',
    key: 'module',
    ellipsis: true,
    customRender: ({ text }) =>
      h(
        'span',
        {
          class:
            'text-[13px] leading-[20.8px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]',
        },
        formatConsumptionModule(String(text ?? '')),
      ),
  },
  {
    title: '服务商',
    dataIndex: 'provider',
    key: 'provider',
    ellipsis: true,
  },
  {
    title: '消耗积分',
    key: 'points',
    width: 160,
    customRender: ({ record }) => {
      if (record.freeTag) {
        return h('span', { class: 'inline-flex items-center gap-2' }, [
          h('span', { class: 'text-sm text-[rgba(0,0,0,0.65)]' }, '0'),
          h(
            'span',
            {
              class:
                'inline-flex h-[22px] items-center rounded-md bg-[rgba(215,215,255,0.40)] px-2.5 py-0.5 text-xs font-semibold leading-[18px] text-[#726FFF]',
            },
            '免费积分',
          ),
        ])
      }
      if (record.freeQuota) {
        return h(
          'span',
          { class: 'text-sm text-[rgba(0,0,0,0.65)]' },
          `${record.points}（免费额度）`,
        )
      }
      return h('span', { class: 'text-sm text-[rgba(0,0,0,0.65)]' }, String(record.points))
    },
  },
])
</script>

<template>
  <div
    class="flex min-h-0 min-w-0 flex-1 flex-col gap-4 self-stretch overflow-hidden"
  >
    <!-- 上图表行：允许饼图 hover 略超出，不被祖先裁切 -->
    <div class="flex shrink-0 gap-4 self-stretch overflow-visible">
      <!-- 今日/本月消耗 + 柱状图 -->
      <div
        class="relative flex min-h-[272px] min-w-0 flex-1 flex-col gap-3 rounded-2xl border border-solid border-[rgba(0,0,0,0.10)] bg-white p-6 dark:border-[rgba(255,255,255,0.14)] dark:bg-[#1a1a1a]"
      >
        <div class="flex h-20 w-full shrink-0 items-start justify-between pr-[140px]">
          <div class="flex flex-col gap-2">
            <span
              class="text-sm font-normal leading-[22px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]"
            >
              {{ consumeTitle }}
            </span>
            <div class="flex items-end gap-2.5">
              <span
                class="font-sans text-[44px] font-bold leading-10 text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]"
              >
                {{ chartTotalPoints.toLocaleString() }}
              </span>
              <span
                class="text-sm font-normal leading-[22px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]"
              >
                积分
              </span>
            </div>
          </div>
        </div>

        <div class="relative min-h-[120px] w-full flex-1">
          <a-spin :spinning="chartLoading" class="min-h-[120px] w-full">
            <VChart class="consume-bar-chart" :option="barChartOption" autoresize />
          </a-spin>
        </div>

        <!-- 今日 / 本月 -->
        <div
          class="absolute right-4 top-4 inline-flex items-center gap-1 rounded-lg border border-solid border-[rgba(0,0,0,0.07)] bg-white p-1 dark:border-[rgba(255,255,255,0.12)] dark:bg-[#1a1a1a]"
        >
          <button
            type="button"
            class="rounded px-2 py-1 text-sm transition-colors"
            :class="
              chartScope === 'today'
                ? 'bg-[rgba(215,215,255,0.40)] text-[rgba(0,0,0,0.85)] dark:bg-[rgba(215,215,255,0.15)] dark:text-[rgba(255,255,255,0.85)]'
                : 'text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]'
            "
            @click="chartScope = 'today'"
          >
            今日
          </button>
          <button
            type="button"
            class="rounded px-2 py-1 text-sm transition-colors"
            :class="
              chartScope === 'month'
                ? 'bg-[rgba(215,215,255,0.40)] text-[rgba(0,0,0,0.85)] dark:bg-[rgba(215,215,255,0.15)] dark:text-[rgba(255,255,255,0.85)]'
                : 'text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]'
            "
            @click="chartScope = 'month'"
          >
            本月
          </button>
        </div>
      </div>

      <!-- 本月消耗分布：外 8px + 内 16px = 24，内层 overflow 放开给饼图 hover 放大 -->
      <div
        class="flex h-[272px] w-[300px] shrink-0 flex-col overflow-visible rounded-2xl border border-solid border-[rgba(0,0,0,0.10)] bg-white dark:border-[rgba(255,255,255,0.14)] dark:bg-[#1a1a1a]"
      >
        <span
          class="shrink-0 px-6 pt-6 text-sm font-normal leading-[22px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]"
        >
          {{ pieDistributionTitle }}
        </span>
        <div class="consume-pie-chart-zone min-h-0 min-w-0 flex-1">
          <div class="box-border h-full w-full p-2">
            <div class="consume-pie-hover-room box-border h-full w-full p-4">
              <a-spin :spinning="chartLoading" class="block h-full min-h-[120px] w-full">
                <VChart class="consume-pie-chart h-full w-full min-h-[120px]" :option="pieChartOption" autoresize />
              </a-spin>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 消耗明细：外框撑满剩余高度，表格在框内滚动 -->
    <div
      class="consume-detail-section flex min-h-0 min-w-0 flex-1 flex-col gap-4 self-stretch overflow-hidden rounded-2xl border border-solid border-[rgba(0,0,0,0.10)] bg-white px-6 pb-6 pt-6 dark:border-[rgba(255,255,255,0.14)] dark:bg-[#1a1a1a]"
    >
      <div class="flex shrink-0 items-start justify-between gap-4 self-stretch">
        <span class="text-base font-semibold leading-[25.6px] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]">
          消耗明细
        </span>
        <div class="flex shrink-0 items-center gap-2">
          <a-select
            v-model:value="moduleFilter"
            :bordered="false"
            :options="moduleFilterSelectOptions"
            class="consume-filter-select h-8 w-[200px] rounded-md"
            :dropdown-match-select-width="false"
            :get-popup-container="consumeSelectGetPopupContainer"
            :dropdown-style="CONSUME_PICKER_POPUP_STYLE"
          >
            <template #option="{ label }">
              {{ moduleFilterDropdownLabel(label) }}
            </template>
            <template #suffixIcon>
              <DownOutlined class="text-[rgba(0,0,0,0.25)]" />
            </template>
          </a-select>
          <a-range-picker
            v-model:value="dateRange"
            :bordered="false"
            class="consume-range-picker h-8 w-[240px] rounded-md"
            :placeholder="['开始日期', '结束日期']"
            :get-popup-container="consumePickerGetPopupContainer"
            :popup-style="CONSUME_PICKER_POPUP_STYLE"
          >
            <template #suffixIcon>
              <CalendarOutlined class="text-[rgba(0,0,0,0.25)]" />
            </template>
          </a-range-picker>
        </div>
      </div>

      <div
        ref="consumeTableFrameRef"
        class="consume-table-frame consume-detail-table-wrap box-border min-h-0 w-full min-w-0 flex-1 overflow-hidden"
      >
        <a-spin :spinning="tableLoading" class="h-full min-h-0 w-full [&_.ant-spin-container]:h-full">
          <Table
            row-key="key"
            :columns="columns"
            :data-source="tableRecords"
            :pagination="false"
            :scroll="consumeTableScroll"
            size="small"
            class="consume-detail-table"
          />
        </a-spin>
      </div>

      <div v-if="tableTotal > 0" class="flex shrink-0 justify-end pt-1">
        <a-pagination
          v-model:current="tablePageNo"
          v-model:page-size="tablePageSize"
          :total="tableTotal"
          :show-size-changer="true"
          size="small"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.consume-bar-chart {
  width: 100%;
  height: 100%;
  min-height: 120px;
}

.consume-pie-chart-zone {
  overflow: visible;
}

.consume-pie-hover-room {
  overflow: visible;
}

.consume-pie-chart {
  width: 100%;
  height: 100%;
  min-height: 120px;
  overflow: visible;
}

.consume-filter-select {
  background: #f3f3f7;

  &:deep(.ant-select-selector) {
    height: 32px;
    padding-inline: 11px;
    background: #f3f3f7;
    border: none;
    border-radius: 6px;
    box-shadow: none;
  }

  &:deep(.ant-select-selection-item) {
    line-height: 30px;
    color: rgba(0, 0, 0, 0.45);
    font-size: 14px;
  }
}

.consume-range-picker {
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

.consume-detail-section {
  box-sizing: border-box;
  flex: 1 1 0;
  min-height: 0;
}

.consume-detail-table-wrap {
  display: flex;
  flex-direction: column;
}

.consume-table-frame {
  flex: 1 1 0;
  min-height: 0;
}

.consume-detail-table {
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
    border-radius: 12px;
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
