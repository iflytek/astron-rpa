<script lang="ts" setup>
import { COLOR_LIST, ROBOT_AVATAR_LIST } from '@/constants/avatar'

import AvatarPicker from './AvatarPicker.vue'
import ColorPicker from './ColorPicker.vue'

const color = defineModel('color', { type: String, required: true })
const icon = defineModel('icon', { type: String, required: true })
</script>

<template>
  <a-form layout="vertical" class="flex-1">
    <a-form-item label="头像图标">
      <AvatarPicker v-model:value="icon" :list="ROBOT_AVATAR_LIST" />
    </a-form-item>
    <a-form-item label="头像背景色">
      <ColorPicker v-model:value="color" :color-list="COLOR_LIST" />
    </a-form-item>
  </a-form>
</template>
