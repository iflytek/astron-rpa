<script setup lang="ts">
import { useTheme } from '@rpa/components'
import { storeToRefs } from 'pinia'
import { defineAsyncComponent, onBeforeMount, onUnmounted } from 'vue'

import { getRootBaseURL } from '@/api/http/env'
import { useProcessStore } from '@/stores/useProcessStore'

const props = defineProps<{ resourceId: string }>()
const processStore = useProcessStore()
const { isDark } = useTheme()
const { pyCodeText } = storeToRefs(processStore)

const baseUrl = `${getRootBaseURL()}/scheduler`
const CodeEditor = defineAsyncComponent(() => import('@rpa/components').then(m => m.CodeEditor))

function handleUpdate(codeString: string) {
  processStore.setCodeText(codeString)
  processStore.savePyCode()
}

onBeforeMount(() => processStore.getPyCodeText(props.resourceId))

onUnmounted(() => processStore.setCodeText(''))
</script>

<template>
  <CodeEditor
    :project-id="processStore.project.id"
    :base-url="baseUrl"
    :value="pyCodeText"
    :is-dark="isDark"
    height="100%"
    @update:value="handleUpdate"
  />
</template>
