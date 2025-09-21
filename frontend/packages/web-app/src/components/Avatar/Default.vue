<script lang="ts" setup>
import { COLOR_LIST } from '@/constants/avatar'

import ColorPicker from './ColorPicker.vue'

const color = defineModel('color', { type: String, required: true })
</script>

<template>
  <ColorPicker v-model:value="color" :color-list="COLOR_LIST" />
</template>
