<script setup lang="ts">
import { MATCH_DEGREE } from '@/views/Arrange/config/atom'

const percent = defineModel<number>('value', { required: true, default: 95 })
</script>

<template>
  <div class="atom-slider w-full flex gap-8">
    <a-slider class="flex-1" v-model:value="percent" :track-style="{ backgroundColor: '#4e68f6' }" :marks="MATCH_DEGREE">
      <template #mark="{ label, point }">
        <template v-if="point === 100">
          <strong>{{ label }}</strong>
        </template>
        <template v-else>
          {{ label }}
        </template>
      </template>
    </a-slider>
    <a-input-number v-model:value="percent" class="atom-slider-number" :min="0" :max="100" :step="1" />
  </div>
</template>

<style lang="scss" scoped>
.atom-slider {
  &-number {
    width: 52px;
    height: 32px;
  }

  :deep(.ant-input-number-input) {
    padding: 8px;
  }
  
  :deep(.ant-slider-mark-text) {
    font-size: 12px;
  }
  :deep(.ant-slider-mark-text:nth-child(2)) {
    transform: translateX(-75%) !important;
  }
  :deep(.ant-slider-mark-text:last-child) {
    transform: translateX(15%) !important;
  }
  :deep(.ant-slider-rail) {
    width: 104% !important;
  }
}
</style>
