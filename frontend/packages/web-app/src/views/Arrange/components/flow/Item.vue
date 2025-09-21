<script setup lang="ts">
import type { PropType } from 'vue'

import TriggerInput from '@/views/Arrange/components/triggerInsert/TriggerInput.vue'

import { useRenderList } from './hooks/useRenderList'
import ItemContent from './ItemContent.vue'

const { item, index } = defineProps({
  item: {
    type: Object as PropType<RPA.Atom>,
  },
  index: {
    type: Number,
  },
})
const emits = defineEmits(['select'])

const { insertItem, insertItemIndex } = useRenderList()

function itemStyle(item: RPA.Atom) {
  return {
    'insert-item': item === insertItem.value,
    'hide-item': item.isHideNode,
  }
}

function clickAtom(key: string) {
  emits('select', key, insertItemIndex.value)
}
</script>

<template>
  <div
    :data-id="item.id"
    :class="itemStyle(item)"
    class="flow-list-item"
  >
    <TriggerInput
      v-if="item.id === 'insertItem'"
      :key="insertItemIndex"
      @select="clickAtom"
    />
    <ItemContent v-else :key="item.id" :item="item" :index="index" />
  </div>
</template>
