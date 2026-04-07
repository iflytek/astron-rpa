<script setup lang="ts">
import { ref } from 'vue'

import type { FormItemProps } from './index'
import AtomPopover from '../AtomPopover.vue'
import AtomVarPopover from '../AtomVarPopover.vue'

const iconStyle = { fontSize: '16px', color: 'inherit' }

const props = defineProps<FormItemProps>()

const open = ref(false)
</script>

<template>
  <AtomPopover v-model:open="open">
    <template #content>
      <AtomVarPopover :render-data="props.item" :var-type="props.item.types" />
    </template>
    <rpa-hint-icon name="open-var-btn" title="选择变量" class="cursor-pointer" :style="iconStyle" />
  </AtomPopover>
</template>
