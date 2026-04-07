<script setup lang="ts">
import TriggerInput from './triggerInsert/TriggerInput.vue'
import { useRenderList } from './hooks/useRenderList'
import ItemContent from './ItemContent.vue'

const props = defineProps<{ item: RPA.Atom, index: number }>()
const emits = defineEmits(['select'])

const { insertItem, insertItemIndex } = useRenderList()

function clickAtom(key: string) {
  emits('select', key, insertItemIndex.value)
}
</script>

<template>
  <div
    :data-id="props.item.id"
    :class="{
      'insert-item': props.item === insertItem.value,
      'hide-item': props.item.isHide,
    }"
    class="flow-list-item"
  >
    <TriggerInput
      v-if="props.item.id === 'insertItem'"
      :key="insertItemIndex"
      @select="clickAtom"
    />
    <ItemContent v-else :key="props.item.id" :item="props.item" :index="props.index" />
  </div>
</template>
