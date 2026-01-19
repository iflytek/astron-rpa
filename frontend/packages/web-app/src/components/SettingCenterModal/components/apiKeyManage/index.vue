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
  <div class="flex flex-col h-full overflow-hidden">
    <div class="mb-3">
      <a-segmented v-model:value="activeKey" :options="options" />
    </div>
    <div class="flex-1">
      <ApiKeyManage v-show="activeKey === 'apiKey'" />
      <AgentKeyManage v-show="activeKey === 'starAgent'" />
    </div>
  </div>
</template>