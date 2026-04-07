<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { ComponentPublishModal } from '@/components/ComponentPublish'
import { PublishModal } from '@/components/PublishComponents'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'

import ToolButton from '../components/ToolButton.vue'

const processStore = useProcessStore()
const runningStore = useRunningStore()
const projectId = useRoute()?.query?.projectId as string

const disabled = computed(() => ['debug', 'run'].includes(runningStore.running))

function handleClick() {
  if (processStore.isComponent) {
    NiceModal.show(ComponentPublishModal, { componentId: projectId })
  } else {
    NiceModal.show(PublishModal, { robotId: projectId })
  }
}
</script>

<template>
  <ToolButton :tooltip="$t('release')" :label="$t('release')" :disabled="disabled" icon="tools-publish" @click="handleClick" />
</template>

