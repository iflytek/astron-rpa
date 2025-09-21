<script setup lang="ts">
import type { AvatarItem } from '@/constants/avatar'

import Avatar from './Avatar.vue'

const props = defineProps<{
  list: AvatarItem[]
}>()
const value = defineModel('value', { type: String, required: true })

function handleChangeAvatar(icon: string) {
  value.value = icon
}
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <a-tooltip v-for="item in props.list" :key="item.name" :title="$t(item.name)">
      <Avatar
        :icon="item.icon"
        size="small"
        hover
        :active="value === item.icon"
        @click="handleChangeAvatar(item.icon)"
      />
    </a-tooltip>
  </div>
</template>
