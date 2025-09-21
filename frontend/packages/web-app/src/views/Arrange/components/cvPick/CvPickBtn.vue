<script lang="ts" setup>
import { computed, ref } from 'vue'

import { useCvPickStore } from '@/stores/useCvPickStore'

import { useCvPick } from './hooks/useCvPick'

const { type, groupId, entry } = defineProps({
  type: {
    type: String,
    default: 'default', // default-默认展示图标和文字 icon-只展示图标 text-只展示文字
  },
  groupId: {
    type: String,
    default: '',
  },
  entry: {
    type: String,
    default: 'group',
  },
})

const emits = defineEmits(['click'])

function cvPick() {
  emits('click')
  useCvPick().pick({ groupId, entry })
}
const cvPickStore = useCvPickStore()
const pickLoading = ref(false)
const pickBtnDisabled = computed(() => cvPickStore.isPicking)
const defaultPickLoading = computed(() => cvPickStore.isPicking === true && pickLoading.value === true)
</script>

<template>
  <rpa-hint-icon
    v-if="type === 'icon'"
    placement="top"
    title="拾取图像"
    name="excel-insert-image"
    :loading="defaultPickLoading"
    :disabled="pickBtnDisabled"
    @click="cvPick"
  />
  <span v-else-if="type === 'text'" @click="cvPick">拾取图像</span>
  <rpa-hint-icon
    v-else name="excel-insert-image"
    :loading="defaultPickLoading"
    :disabled="pickBtnDisabled"
    enable-hover-bg
    @click="cvPick"
  >
    <template #suffix>
      <span class="ml-1">拾取图像</span>
    </template>
  </rpa-hint-icon>
</template>
