<script setup lang="ts">
import { ref, computed } from 'vue'

import CvPopover, { type SelectedElement } from '../../cvPick/CvPopover.vue'
import type { FormItemProps, FormItemEmits } from './index'
import AtomPopover from '../AtomPopover.vue'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const open = ref(false)
const chosedValue = computed(() => props.item.value[0]?.data)

function closePopover() {
  open.value = false
}

function handleSelect(selected: SelectedElement[]) {
  emits('update', props.item.key, selected)
}
</script>

<template>
  <AtomPopover v-model:open="open" tooltip="选择元素">
    <span class="w-5 h-5 flex justify-center items-center relative cursor-pointer">
      <rpa-icon size="16" name="bottom-menu-ele-manage" />
    </span>

    <template #content>
      <CvPopover 
        :render-data="props.item"
        :item-chosed="chosedValue"
        @close="closePopover"
        @select="handleSelect"
      />
    </template>
  </AtomPopover>
</template>
