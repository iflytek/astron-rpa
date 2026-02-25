<script setup lang="ts">
import { useTheme, CodeEditor as CodeEditorComponent } from '@rpa/components'

import { getBaseURL } from '@/api/http/env'

import { useCodeState } from './useCodeState'
import { CodeEditor } from '../../canvasManager'

interface ProcessCodeProps {
  resourceId: string
  manage: CodeEditor
}

const props = defineProps<ProcessCodeProps>()
const { projectId, updateCode } = useCodeState(props)
const { isDark } = useTheme()

const baseUrl = `${getBaseURL()}/scheduler`
</script>

<template>
  <CodeEditorComponent
    :project-id="projectId"
    :base-url="baseUrl"
    :value="props.manage.state.data"
    :is-dark="isDark"
    height="100%"
    @update:value="updateCode"
  />
</template>
