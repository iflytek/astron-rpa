<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { computed, ref } from 'vue'

import AgentKeyManage from './AgentKeyManage.vue'
import ApiKeyManage from './ApiKeyManage.vue'

const activeKey = ref('apiKey')
const { t } = useTranslation()

const options = computed(() => ([
  {
    label: t('settingCenter.apiKeyManage.rpaAuthManage'),
    value: 'apiKey',
  },
  {
    label: t('settingCenter.apiKeyManage.agentAuthManage'),
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
