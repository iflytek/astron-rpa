<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

import { ATOM_KEY_MAP } from '@/constants/atom'

const props = defineProps<{ item: RPA.Atom }>()

const { t } = useTranslation()

const isGroup = computed(() => {
  return props.item.key === ATOM_KEY_MAP.Group || props.item.key === ATOM_KEY_MAP.GroupEnd
})

const isGroupStart = computed(() => props.item.key === ATOM_KEY_MAP.Group)

const iconName = computed(() => {
  if (isGroupStart.value) {
    return 'group-start'
  }
  if (props.item.key === ATOM_KEY_MAP.GroupEnd) {
    return 'group-end'
  }
  return props.item.icon
})

const displayText = computed(() => {
  return props.item.alias || props.item.title || ''
})

const groupSuffix = computed(() => {
  return isGroupStart.value ? t('groupStart') : t('groupEnd')
})
</script>

<template>
  <div class="inline font-semibold">
    <rpa-hint-icon
      v-if="iconName"
      :name="iconName"
      class="inline-block mr-1 text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65] relative top-[2px]"
    />
    <span v-else class="mr-1 w-4 h-4 inline-block" />
    <template v-if="isGroup">
      <span class="text-primary">{{ displayText }}</span>
      {{ groupSuffix }}
    </template>
    <span v-else>{{ displayText }}</span>
  </div>
</template>
