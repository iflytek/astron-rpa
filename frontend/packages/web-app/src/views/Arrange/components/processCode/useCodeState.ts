import { computed } from "vue"

import { useProcessStore } from '@/stores/useProcessStore'

import type { CodeEditor } from '../../canvasManager'

interface InitParams {
  resourceId: string
  manage: CodeEditor
}

export const useCodeState = (params: InitParams) => {
  const processStore = useProcessStore()

  const projectId = computed(() => processStore.project.id)

  const updateCode = (code: string) => params.manage.updateCode(code)

  return { projectId, updateCode }
}
