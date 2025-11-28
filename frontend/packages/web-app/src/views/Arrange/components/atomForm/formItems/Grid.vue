<script setup lang="ts">
import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const hanldeSelect = (item: number) => {
  emits('update', props.item.key, item)
}
</script>

<template>
  <section class="atom-grid cursor-pointer flex justify-center align-items">
    <div v-for="item in 9" :key="item" class="atom-grid-item relative" :class="{ active: props.item.value === item }" @click="hanldeSelect(item)" />
  </section>
</template>

<style lang="scss" scoped>
.atom-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
  padding-left: 10px;
  &-item {
    width: 30px;
    height: 30px;
    border: 1px solid #ccc;
    border-radius: 4px;
    text-align: center;
    &.active,
    &:hover {
      background-color: #f8f8f8;
      &:before {
        content: 'x';
        line-height: 30px;
        color: #ccc;
      }
    }
  }
}
</style>
