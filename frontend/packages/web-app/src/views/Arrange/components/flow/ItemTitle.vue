<script setup lang="ts">
import { computed } from 'vue'

import { Group, GroupEnd } from '@/views/Arrange/config/atomKeyMap'

const { item } = defineProps<{ item: RPA.Atom }>()

const iconName = computed(() => {
  switch (item.key) {
    case Group:
      return 'group-start'
    case GroupEnd:
      return 'group-end'
    default:
      return item.icon
  }
})
</script>

<template>
  <div class="inline font-medium">
    <rpa-hint-icon
      :name="iconName"
      class="inline-block mr-1 text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65] relative top-[2px]"
    />
    <span v-if="item.key === Group || item.key === GroupEnd">
      <span class="text-primary">{{ item.alias || item.title }}</span>
      <template v-if="item.key === Group"> 编组开始</template>
      <template v-else> 编组结束</template>
    </span>
    <span v-else>{{ item.alias || item.title }}</span>
  </div>
</template>
