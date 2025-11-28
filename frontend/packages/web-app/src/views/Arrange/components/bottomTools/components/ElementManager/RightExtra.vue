<script lang="ts" setup>
import { throttle } from 'lodash-es'

import { usePickStore } from '@/stores/usePickStore'

import ManageHeader from '../ManageHeader.vue'

import ElementBtns from './ElementBtns.vue'

const usePick = usePickStore()

// 拾取新元素
const pickNewElement = throttle(() => {
  usePick.newPick('')
}, 1000, { leading: true, trailing: false })
</script>

<template>
  <ManageHeader :placeholder="$t('searchElements')">
    <template #btns>
      <ElementBtns :loading="usePick.isPicking" :disabled="usePick.isPicking" @click="pickNewElement" />
    </template>
  </ManageHeader>
</template>
