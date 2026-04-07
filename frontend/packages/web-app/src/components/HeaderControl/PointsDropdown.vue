<script setup lang="ts">
import { ArrowRightOutlined } from '@ant-design/icons-vue'
import { computed } from 'vue'

import { TENANT_EDITION, TENANT_EDITION_LABEL, type TenantEditionKey } from './tenantEdition'

const props = withDefaults(
  defineProps<{
    /** 当前租户套餐 */
    planEdition?: TenantEditionKey
    /** 积分数量 */
    points?: number
    /** 周免费剩余额度（与接口 freeQuota.weeklyRemaining 一致） */
    dialogueCount?: number
    /** 有值时覆盖底部灰色提示（如接口 resetTime） */
    quotaResetHint?: string
  }>(),
  {
    planEdition: TENANT_EDITION.Personal,
    points: 2000,
    dialogueCount: 50,
  },
)

const editionLabel = computed(() => TENANT_EDITION_LABEL[props.planEdition])

const showUpgradeCta = computed(() => props.planEdition === TENANT_EDITION.Personal)

const emit = defineEmits<{
  usageDetails: []
  upgrade: []
}>()

const formattedPoints = computed(() => `${props.points.toLocaleString()} 分`)

const dialogueLabel = computed(() => `${props.dialogueCount} 次`)

const resetHintText = computed(
  () => `每周一 0 点重置 ${props.dialogueCount} 次对话额度`,
)
</script>

<template>
  <div
    class="flex w-80 flex-col gap-2 overflow-hidden rounded-2xl bg-white p-2 shadow-[0px_4px_6px_-2px_rgba(10,13,18,0.03),0px_12px_16px_-4px_rgba(10,13,18,0.08)] dark:bg-[#141414]"
  >
    <div class="flex w-full items-center justify-between px-2 py-2">
      <span class="text-center text-base font-medium text-black/[0.85] dark:text-white/[0.85]">
        {{ editionLabel }}
      </span>
      <button
        type="button"
        class="inline-flex cursor-pointer items-center gap-2 border-0 bg-transparent p-0 text-sm font-normal text-black/[0.65] hover:opacity-80 dark:text-white/[0.65]"
        @click="emit('usageDetails')"
      >
        <span>使用详情</span>
        <ArrowRightOutlined class="text-xs" />
      </button>
    </div>

    <div class="flex w-full flex-col rounded-xl bg-[#F3F3F7] dark:bg-white/[0.08]">
      <div class="inline-flex w-full items-center justify-between px-3 py-3">
        <div class="inline-flex items-center gap-1">
          <rpa-icon name="ai" color="#726fff" size="16" class="shrink-0" />
          <span class="text-center text-sm font-normal text-black/[0.85] dark:text-white/[0.85]">
            积分
          </span>
        </div>
        <span class="text-center text-sm font-normal text-black/[0.65] dark:text-white/[0.65]">
          {{ formattedPoints }}
        </span>
      </div>

      <div
        class="flex w-full flex-col gap-1 px-3 py-3 [border-top:1px_dashed_rgba(0,0,0,0.04)] dark:[border-top:1px_dashed_rgba(255,255,255,0.08)]"
      >
        <div class="inline-flex w-full items-center justify-between gap-2">
          <div class="inline-flex min-w-0 items-center gap-1">
            <rpa-icon name="magic-wand" color="#726fff" size="16" class="shrink-0" />
            <span class="text-center text-sm font-normal text-black/[0.85] dark:text-white/[0.85]">
              智能组件可对话次数
            </span>
          </div>
          <span
            class="shrink-0 text-center text-sm font-normal text-black/[0.65] dark:text-white/[0.65]"
          >
            {{ dialogueLabel }}
          </span>
        </div>
        <div
          class="inline-flex items-center justify-center pl-5 text-center text-xs font-normal !text-[rgba(0,0,0,0.25)] dark:!text-[rgba(255,255,255,0.25)]"
        >
          {{ props.quotaResetHint ?? resetHintText }}
        </div>
      </div>
    </div>

    <button
      v-if="showUpgradeCta"
      type="button"
      class="inline-flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl border-0 px-4 py-3 shadow-[inset_0_-2px_4px_rgba(255,255,255,0.2)] [background:linear-gradient(90deg,rgba(199,181,252,0.2)_0%,rgba(81,71,255,0.1)_60%,rgba(199,181,252,0.3)_100%)] hover:opacity-95 dark:[background:linear-gradient(90deg,rgba(199,181,252,0.15)_0%,rgba(81,71,255,0.12)_60%,rgba(199,181,252,0.2)_100%)]"
      @click="emit('upgrade')"
    >
      <span class="text-center text-sm font-semibold leading-5 text-[#726FFF]">
        升级为专业版/企业版
      </span>
    </button>
  </div>
</template>
