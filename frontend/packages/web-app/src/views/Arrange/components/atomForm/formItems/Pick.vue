<script setup lang="ts">
import { ref } from 'vue'

import type { FormItemEmits, FormItemProps } from './index'
import ElePopover from '../../pick/ElePopover.vue'
import AtomPopover from '../components/AtomPopover.vue'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()
const open = ref(false)

function closePopover() {
  open.value = false
}

function handleSelect(data: RPA.AtomFormItemResult[]) {
  emits('update', props.item.key, data)
  closePopover()
}
</script>

<template>
  <AtomPopover v-model:open="open" tooltip="选择元素">
    <a-button type="text" class="flex justify-center items-center panel-bg">
      <template #icon>
        <rpa-icon size="16" name="bottom-menu-ele-manage" />
      </template>
    </a-button>

    <template #content>
      <ElePopover :render-data="props.item" @close="closePopover" @select="handleSelect" />
    </template>
  </AtomPopover>
</template>
