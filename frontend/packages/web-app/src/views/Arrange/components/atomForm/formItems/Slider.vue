<script setup lang="ts">
import { computed } from 'vue';
import { isNumber } from 'lodash-es'

import type { FormItemProps } from './index'
import AtomSlider from '../AtomSlider.vue'

const props = defineProps<FormItemProps>()

const percent = computed(() => {
  if (isNumber(props.item.value)) {
    return props.item.value * 100
  }

  return 95
})
</script>

<template>
  <AtomSlider :value="percent" />
</template>
