<script setup lang="ts">
import { ref } from 'vue'

import { ATOM_FORM_TYPE } from '@/constants/atom'

import AtomColorPopover from './AtomColorPopover.vue'
import AtomCvPopover from './AtomCvPopover.vue'
import AtomElePopover from './AtomElePopover.vue'
import AtomVarPopover from './AtomVarPopover.vue'

defineProps<{
  renderType?: string
  renderData: RPA.AtomDisplayItem
  varType?: string
  tooltip?: string
}>()

const openPopover = ref(false)
</script>

<template>
  <a-popover
    v-model:open="openPopover"
    class="atom-popover"
    placement="topLeft"
    trigger="click"
    :destroy-tooltip-on-hide="true"
    :overlay-style="{ zIndex: 1001 }"
  >
    <template #content>
      <AtomVarPopover
        v-if="renderType === ATOM_FORM_TYPE.VARIABLE"
        :render-data="renderData"
        :var-type="varType"
      />
      <AtomElePopover
        v-if="renderType === ATOM_FORM_TYPE.PICK"
        :render-data="renderData"
        @close-popover="openPopover = false"
      />
      <AtomCvPopover
        v-if="renderType === ATOM_FORM_TYPE.CV_IMAGE"
        :render-data="renderData"
        :item-chosed="renderData.value[0]?.data"
        @close-popover="openPopover = false"
      />
      <AtomColorPopover
        v-if="renderType === ATOM_FORM_TYPE.COLOR"
        :render-data="renderData"
        @close-popover="openPopover = false"
      />
    </template>

    <a-tooltip v-if="tooltip" :title="tooltip">
      <slot />
    </a-tooltip>
    <slot v-else />
  </a-popover>
</template>

<style lang="scss" scoped>
.atom-popover {
  .atom-popover-footer {
    border-top: 1px solid #f0f0f0;
  }
}

:deep(.ant-popover) {
  display: none;
}

:deep(.ant-popover-content) {
  display: none;
}
</style>
