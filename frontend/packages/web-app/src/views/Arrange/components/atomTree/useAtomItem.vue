<script setup lang="ts">
import { toUpper } from 'lodash-es'
import { computed } from 'vue'

import type { LanguageType } from '@/plugins/i18next'
import { translate } from '@/plugins/i18next'

const props = defineProps<{
  title: string | LanguageType
  icon?: string
  iconColor?: string
  searchAtom?: string
  dot?: boolean
}>()

const titleText = computed(() => translate(props.title))
const idx = computed(() => toUpper(titleText.value).indexOf(toUpper(props.searchAtom)))
</script>

<template>
  <div class="flex-1 flex items-center text-[12px] overflow-hidden gap-1">
    <template v-if="icon">
      <a-badge :dot="dot" class="dot inline-flex">
        <rpa-hint-icon :name="icon" :color="iconColor" />
      </a-badge>
    </template>
    <template v-if="searchAtom && idx >= 0">
      <span class="text-ellipsis whitespace-nowrap overflow-hidden">
        <span>{{ titleText.substring(0, idx) }}</span>
        <span class="text-primary font-bold">{{ titleText.substring(idx, idx + searchAtom.length) }}</span>
        <span>{{ titleText.substring(idx + searchAtom.length) }}</span>
      </span>
    </template>
    <template v-else>
      <span class="text-ellipsis whitespace-nowrap overflow-hidden">{{ titleText }}</span>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.dot {
  :deep(.ant-badge-dot) {
    width: 4px;
    min-width: 4px;
    height: 4px;
  }
}
</style>
