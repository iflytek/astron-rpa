<script lang="ts" setup>
import { useTranslation } from 'i18next-vue'

import { WEEK_MAP_EN, WEEK_OPTIONS } from '../../config/task'

const { value = [] } = defineProps<{ value: Array<string | number> }>()

defineEmits(['update:value'])

const { t } = useTranslation()
const weekOptions = WEEK_OPTIONS.map((it) => {
  return { label: t(`weekOptions.${WEEK_MAP_EN[it.value]}`), value: it.value }
})
</script>

<template>
  <a-select :max-tag-count="3" :options="weekOptions" :value="value" class="weekday-picker text-[12px]" mode="multiple" :placeholder="t('weekSelectPlaceholder')" @change="(val) => $emit('update:value', val)" />
</template>
