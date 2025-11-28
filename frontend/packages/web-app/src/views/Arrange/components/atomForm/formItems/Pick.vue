<script setup lang="ts">
import { ref } from 'vue'

import type { FormItemProps } from './index'
import ElePopover from '../../pick/ElePopover.vue'
import AtomPopover from '../AtomPopover.vue'

const props = defineProps<FormItemProps>()
const open = ref(false)

function closePopover() {
  open.value = false
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
      <ElePopover :render-data="props.item" @close="closePopover" />
    </template>
  </AtomPopover>
</template>
