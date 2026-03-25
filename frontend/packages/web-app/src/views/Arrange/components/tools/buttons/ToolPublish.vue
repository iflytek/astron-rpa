<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import { useRoute } from 'vue-router'
import { useTranslation } from 'i18next-vue'

import { ComponentPublishModal } from '@/components/ComponentPublish'
import { PublishModal } from '@/components/PublishComponents'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'

import ToolButton from '../components/ToolButton.vue'

const processStore = useProcessStore()
const runningStore = useRunningStore()
const projectId = useRoute()?.query?.projectId as string
const { t } = useTranslation()

const show = computed(() => true)
const disabled = computed(() => ['debug', 'run'].includes(runningStore.running))

function handleClick() {
  if (disabled.value) {
    message.warning(t('toolsTips.runningOrDebuggingTryLater'))
    return
  }
  if (processStore.isComponent) {
    NiceModal.show(ComponentPublishModal, { componentId: projectId })
  } else {
    NiceModal.show(PublishModal, { robotId: projectId })
  }
}
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('release')" :label="$t('release')" :disabled="disabled" icon="tools-publish" @click="handleClick" />
</template>

