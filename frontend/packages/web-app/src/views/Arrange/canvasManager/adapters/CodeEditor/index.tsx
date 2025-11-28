import { markRaw, shallowReactive } from 'vue'

import { getProcessPyCode, saveProcessPyCode, renameProcessPyCode } from '@/api/resource'

import FlowCode from '../../../components/processCode/Code.vue'
import { UndoManager } from './UndoManager'

type CodeEditorState = RPA.Process.ProcessModule<string>

export class CodeEditor implements RPA.Process.TabInstance<string> {
  id: string
  state: CodeEditorState
  component = markRaw(FlowCode)
  /** 撤销管理 */
  undoManager: UndoManager

  constructor(
    public projectId: string,
    config: RPA.Process.ProcessModule,
  ) {
    this.id = config.resourceId
    this.state = shallowReactive(config)
    this.undoManager = new UndoManager(this)
    this.init()
  }

  async init() {
    this.state.data = await getProcessPyCode({ robotId: this.projectId, moduleId: this.id })
  }

  updateState(updates: Partial<CodeEditorState>): void {
    Object.assign(this.state, updates)
  }

  updateCode(code: string) {
    this.undoManager.update(code)
  }

  /**
   * 重命名
   * @param name 新名称
   */
  async rename(name: string) {
    await renameProcessPyCode({ robotId: this.projectId, moduleId: this.id, moduleName: name })
    this.updateState({ name })
  }

  getActionState(actionType: RPA.Process.TabActionType): RPA.Process.TabActionState {
    const defaultState: RPA.Process.TabActionState = {
      visible: true,
      disabled: false,
    }

    if (['multiSelect', 'group', 'ungroup'].includes(actionType)) {
      defaultState.disabled = true
    }

    return defaultState
  }

  save(): Promise<boolean> {
    return saveProcessPyCode({
      moduleId: this.id,
      robotId: this.projectId,
      moduleContent: this.state.data,
    })
  }
}
