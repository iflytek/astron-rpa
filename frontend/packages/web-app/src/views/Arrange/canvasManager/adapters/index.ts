import { addProcess, addProcessPyCode, genProcessName, genProcessPyCodeName } from '@/api/resource'

import { VisualEditor } from './VisualEditor'
import { CodeEditor } from './CodeEditor'

type Adapter = VisualEditor | CodeEditor
type AdapterType = RPA.Process.ProcessModuleType

interface AdapterConfig {
  newInstance: (projectId: string, config: RPA.Process.ProcessModule) => RPA.Process.TabInstance
  genName: (projectId: string) => Promise<string>
  create: (projectId: string, name: string) => Promise<string>
}

const adapterConfig: Record<AdapterType, AdapterConfig> = {
  process: {
    newInstance: (projectId, config) => new VisualEditor(projectId, config),
    genName: (projectId) => genProcessName({ robotId: projectId }),
    create: (projectId, name) => addProcess({ robotId: projectId, processName: name }),
  },
  module: {
    newInstance: (projectId, config) => new CodeEditor(projectId, config),
    genName: (projectId) => genProcessPyCodeName({ robotId: projectId }),
    create: (projectId, name) => addProcessPyCode({ robotId: projectId, moduleName: name }),
  },
}

/**
 * 创建 tab 实例
 * 根据 resourceCategory 自动选择对应的 adapter
 */
export function newTabInstance(projectId: string, config: RPA.Process.ProcessModule): RPA.Process.TabInstance {
  return adapterConfig[config.resourceCategory].newInstance(projectId, config)
}

export async function createTabInstance(projectId: string, type: RPA.Process.ProcessModuleType, name: string) {
  return adapterConfig[type].create(projectId, name)
}

export async function genName(projectId: string, type: RPA.Process.ProcessModuleType) {
  return adapterConfig[type].genName(projectId)
}

export type { Adapter, VisualEditor, CodeEditor }
