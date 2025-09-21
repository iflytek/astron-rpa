<script setup lang="ts">
import { isNil } from 'lodash-es'
import { storeToRefs } from 'pinia'
import { h } from 'vue'

import { useAppConfigStore } from '@/stores/useAppConfig'
import { useRunningStore } from '@/stores/useRunningStore'
import type { TableMoreAction, TableOrdinaryAction } from '@/views/Home/types'

const props = defineProps({
  row: {
    type: Object,
    default: () => ({}),
  },
  baseOpts: {
    type: Array<TableOrdinaryAction>,
    default: () => [],
  },
  moreOpts: {
    type: Array<TableMoreAction>,
    default: () => [],
  },
})

const { running } = storeToRefs(useRunningStore())
const { colorTheme } = storeToRefs(useAppConfigStore())

function isDisabled(key: string) {
  // 存在运行中的工程，不可编辑和再次运行
  if (running.value === 'run' && ['edit', 'run'].includes(key)) {
    return true
  }

  if (key === 'edit' && !isNil(props.row.editEnable)) {
    return !(props.row.editEnable === 1)
  }

  return false
}

function disableFn(opt) {
  const { row } = props
  return opt.disableFn && opt.disableFn(row)
}
</script>

<template>
  <div class="flex items-center gap-4">
    <template v-for="opt in baseOpts" :key="opt.key">
      <a-tooltip :title="$t(opt.text)">
        <a-button
          size="small"
          class="flex items-center justify-center border-none bg-transparent"
          :disabled="isDisabled(opt.key)"
          :icon="h(opt.icon)"
          @click="() => opt.clickFn(row)"
        />
      </a-tooltip>
    </template>
    <a-dropdown>
      <template #overlay>
        <a-menu :class="[colorTheme]">
          <template v-for="opt in moreOpts" :key="opt.key">
            <a-menu-item :disabled="isDisabled(opt.key) || disableFn(opt)" :icon="h(opt.icon)" @click="() => opt.clickFn(row)">
              <a-tooltip v-if="disableFn(opt) && opt.disableTip" :title="$t(opt.disableTip)">
                {{ $t(opt.text) }}
              </a-tooltip>
              <template v-else>
                {{ $t(opt.text) }}
              </template>
            </a-menu-item>
          </template>
        </a-menu>
      </template>
      <a-button size="small" class="flex items-center justify-center border-none bg-transparent">
        <template #icon>
          <rpa-icon name="ellipsis" size="16px" />
        </template>
      </a-button>
    </a-dropdown>
  </div>
</template>

<style lang="scss" scoped>
:deep(.ant-dropdown-menu-item-active) {
  background-color: rgba(215, 215, 255, 0.4) !important;
}

.dark {
  :deep(.ant-dropdown-menu-item-active) {
    background-color: rgba(93, 89, 255, 0.35) !important;
  }
}
</style>
