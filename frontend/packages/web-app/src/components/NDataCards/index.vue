<script setup lang="ts">
import { useTheme } from '@rpa/components'
import type { PropType } from 'vue'

export interface DataCardItem {
  id: number
  parentCode: string
  icon: string
  field: string
  text: string
  num: string
  unit: string
  percent: string
  tip: string
  order: number
}

const props = defineProps({
  list: {
    type: Array as PropType<DataCardItem[]>,
    default: () => [],
  },
})

const { colorTheme } = useTheme()
</script>

<template>
  <div id="DataCards" class="nDataCards" :class="[colorTheme]">
    <div v-if="props.list.length > 0" class="flex p-4 gap-2">
      <template v-for="item in props.list" :key="item.id">
        <div v-if="item.field === 'executeTotal'" class="flex flex-col gap-2 pt-4 pb-3">
          <div>
            <span>{{ item.text.replace('次数', '') }}</span>
            <span class="text-[11px]"> (次数)</span>
          </div>
          <span class="text-[28px] leading-[28px] font-bold">{{ item.num }}</span>
        </div>
        <div v-else class="relative flex-1 flex flex-col  gap-2 pt-4 pb-3 pl-[18px] bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.04] rounded-[10px] overflow-hidden">
          <div class="flex gap-[6px]">
            <rpa-icon v-if="item.field === 'executeSuccess'" name="success" size="20" />
            <rpa-icon v-if="item.field === 'executeFail'" name="error" size="19" />
            <rpa-icon v-if="item.field === 'executeAbort'" name="stop" size="20" />
            <span class="text-[12px]">{{ item.text.replace(/累计|次数/g, '') }}</span>
          </div>
          <div class="flex items-end gap-[6px]">
            <span class="text-[28px] leading-[28px] font-bold">{{ item.num }}</span>
            <span>{{ item.percent.replace('占比', '') }}</span>
          </div>
          <rpa-icon :name="item.icon" size="54" class="absolute right-[-4px] bottom-[8px]" />
        </div>
      </template>
    </div>

    <div v-else class="nDataCards-empty">
      <div>{{ $t('noData') }}</div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.nDataCards {
  min-height: 90px;
  position: relative;
  border-radius: 14px;
  background: linear-gradient(111deg, #f6f8ff 1.82%, #ececff 100%);

  &.dark {
    background: linear-gradient(111deg, rgba(20, 23, 31, 0.5) 1.82%, rgba(17, 17, 34, 0.5) 100%);
  }

  &-empty {
    width: 100%;
    min-height: 90px;
    color: gray;
    font-size: 14px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}
</style>
