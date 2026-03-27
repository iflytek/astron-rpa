<script setup lang="ts">
import type { PropType } from 'vue'

import type { StudioArtifactPreviewPayload, StudioSummaryItem, StudioTableRow } from '../types'

const props = defineProps({
  preview: {
    type: Object as PropType<StudioArtifactPreviewPayload>,
    required: true,
  },
  compact: {
    type: Boolean,
    default: false,
  },
})

function summaryTone(tone?: StudioSummaryItem['tone']) {
  if (tone === 'danger')
    return 'text-[#DC2626]'
  if (tone === 'success')
    return 'text-[#16A34A]'
  return 'text-black/64'
}

function tableRowTone(tone?: StudioTableRow['tone']) {
  if (tone === 'danger')
    return 'bg-[rgba(254,242,242,0.92)]'
  if (tone === 'success')
    return 'bg-[rgba(240,253,244,0.92)]'
  return 'bg-[rgba(255,255,255,0.9)]'
}
</script>

<template>
  <div
    data-testid="artifact-preview-surface"
    class="space-y-2.5 bg-white/68"
    :class="compact ? 'p-3.5' : 'p-4'"
  >
    <div>
      <div class="text-[11px] font-semibold leading-4 tracking-[-0.01em] text-black/72">
        {{ preview.title }}
      </div>
      <div v-if="preview.description" class="mt-1 text-[10px] leading-4 text-black/40">
        {{ preview.description }}
      </div>
    </div>

    <template v-if="preview.kind === 'code'">
      <div class="overflow-hidden rounded-[14px] bg-[#1E1E2E] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.06)]">
        <div class="flex items-center justify-between border-b border-white/10 px-3 py-2 text-[10px] leading-3 text-white/60">
          <span>{{ preview.fileName }}</span>
          <span>{{ preview.language?.toUpperCase() || 'CODE' }}</span>
        </div>
        <pre class="overflow-x-auto p-3 text-[11px] leading-5 text-[#CDD6F4]"><code>{{ preview.code }}</code></pre>
      </div>
    </template>

    <template v-else-if="preview.kind === 'summary'">
      <div class="space-y-2">
        <div
          v-for="item in preview.items || []"
          :key="item.label"
          class="rounded-[12px] bg-[rgba(255,255,255,0.9)] px-3 py-2.5 shadow-[0_6px_16px_rgba(15,23,42,0.025)]"
        >
          <div class="text-[10px] leading-3 text-black/36">{{ item.label }}</div>
          <div class="mt-1.5 text-[11px] font-medium leading-4" :class="summaryTone(item.tone)">{{ item.value }}</div>
        </div>
      </div>
    </template>

    <template v-else-if="preview.kind === 'table'">
      <div class="overflow-hidden rounded-[14px] bg-[rgba(248,249,252,0.9)] shadow-[inset_0_0_0_1px_rgba(226,231,240,0.86)]">
        <div class="grid gap-px bg-[rgba(226,231,240,0.86)]" :style="{ gridTemplateColumns: `repeat(${preview.columns?.length || 1}, minmax(0, 1fr))` }">
          <div
            v-for="column in preview.columns || []"
            :key="column"
            class="bg-[rgba(245,247,252,0.96)] px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.06em] text-black/36"
          >
            {{ column }}
          </div>
          <template v-for="row in preview.rows || []" :key="row.id">
            <div
              v-for="(cell, index) in row.cells"
              :key="`${row.id}-${index}`"
              class="px-3 py-2.5 text-[11px] leading-4 text-black/68"
              :class="tableRowTone(row.tone)"
            >
              {{ cell }}
            </div>
          </template>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="space-y-2">
        <div
          v-for="row in preview.chartRows || []"
          :key="row.label"
          class="flex items-center gap-2"
        >
          <div class="w-12 shrink-0 text-right text-[10px] leading-3 text-black/34">
            {{ row.label }}
          </div>
          <div class="h-4 grow overflow-hidden rounded-md bg-[#E8EAF2]">
            <div
              class="h-full rounded-md"
              :class="row.over ? 'bg-[#EF4444]' : 'bg-[var(--color-primary)]'"
              :style="{ width: `${Math.min(row.value, 100)}%` }"
            />
          </div>
          <div class="w-8 shrink-0 text-[10px] font-medium leading-3" :class="row.over ? 'text-[#EF4444]' : 'text-[var(--color-primary)]'">
            {{ row.value }}%
          </div>
        </div>

        <div v-if="preview.legend?.length" class="flex flex-wrap items-center gap-3 pt-1 text-[10px] leading-3 text-black/36">
          <span v-for="legend in preview.legend" :key="legend.label" class="flex items-center gap-1">
            <span class="inline-block h-2 w-2 rounded-sm" :style="{ backgroundColor: legend.color }" />
            {{ legend.label }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>
