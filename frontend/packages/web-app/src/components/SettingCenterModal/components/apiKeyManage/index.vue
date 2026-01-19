<script setup lang="ts">
import { computed, ref } from 'vue'

import AgentKeyManage from './AgentKeyManage.vue'
import ApiKeyManage from './ApiKeyManage.vue'

const activeKey = ref('apiKey')

const options = computed(() => ([
  {
    label: '星辰RPA授权管理',
    value: 'apiKey',
  },
  {
    label: '星辰Agent授权管理',
    value: 'starAgent',
  },
]))
</script>

<template>
  <a-segmented v-model:value="activeKey" :options="options" class="mb-3" />
  <ApiKeyManage v-show="activeKey === 'apiKey'" />
  <AgentKeyManage v-show="activeKey === 'starAgent'" />
</template>