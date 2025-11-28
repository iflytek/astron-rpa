declare namespace RPA {
  namespace Process {
    import type { Component, Ref } from 'vue'

    /** 节点配置表单 start */
    interface AtomDisplayBaseConfig {
      name?: object
      key: string
      formItems: RPA.AtomDisplayItem[]
      id?: string
      atomKey?: string
      value?: RPA.AtomFormItemResult[]
    }
    
    interface AtomDisplayConfig {
      baseParam: AtomDisplayBaseConfig[]
      advancedParam: AtomDisplayBaseConfig[]
      exceptParam: AtomDisplayBaseConfig[]
    }
    
    interface AtomTabs {
      key: string
      name: string
      params: AtomDisplayBaseConfig[]
    }
    /** 节点配置表单 end */

    type ProcessModuleType = 'process' | 'module'

    interface ProcessModule<T = any> {
      resourceCategory: ProcessModuleType
      name: string
      resourceId: string
      isSaveing?: boolean
      /** 是否是主流程 */
      isMain?: boolean
      /** 是否正在加载 */
      isLoading?: boolean
      /** 是否已修改（用于显示未保存标记） */
      isDirty?: boolean
      /** 是否已保存 */
      isSaved?: boolean
      /** 是否需要渲染 */
      shouldRender?: boolean
      /** 是否开启多选 */
      multiSelect?: boolean
      /** 当前选中的原子能力ID列表 */
      selectedAtomIds?: string[]
      /** 数据 */
      data?: T
    }

    /**
     * Tab 操作类型
     */
    type TabActionType = 'save' | 'run' | 'debug' | 'multiSelect' | 'group' | 'ungroup' | string

    /**
     * Tab 操作状态
     */
    interface TabActionState {
      /** 是否显示 */
      visible: boolean
      /** 是否禁用 */
      disabled: boolean
      /** 是否加载中 */
      loading?: boolean
      /** 工具提示文本 */
      tooltip?: string
    }

    /**
     * Tab 操作定义
     */
    interface TabAction {
      /** 操作唯一标识 */
      key: TabActionType
      /** 操作图标 */
      icon: string
      /** 操作标题 */
      title: string
      /** 快捷键 */
      hotkey?: string
      /** 获取操作状态 */
      getState?: (tab: TabInstance) => TabActionState | Promise<TabActionState>
      /** 执行操作 */
      execute?: (tab: TabInstance) => void | Promise<void>
    }

    interface ConfigParameter {
      parameters: Ref<RPA.ConfigParamData[]>;
      create(): Promise<void>
      delete(item: RPA.ConfigParamData): Promise<void>
      update(data: RPA.ConfigParamData): Promise<void>
    }

    interface UndoManager {
      canUndo: Ref<boolean>
      canRestore: Ref<boolean>
      undo(): boolean
      restore(): boolean
    }

    interface NodeParameter {
      activeAtomId: Ref<string | undefined>
      activeAtom: RPA.Atom | null
      formTabs: Ref<RPA.Process.AtomTabs[]>
      updateValue(key: string, value: any): void
    }
   
    /**
     * Tab 实例接口
     * 每个 tab 需要实现这个接口来提供操作能力
     */
    interface TabInstance<T = any> {
      /** Tab 唯一标识 */
      id: string
      /** Tab 状态 */
      state: ProcessModule<T>
      /** Tab 内容组件 */
      component: Component
      /** 配置参数管理 */
      configParameter?: ConfigParameter
      /** 节点参数管理 */
      nodeParameter?: NodeParameter
      /** 撤销管理 */
      undoManager: UndoManager

      init(): Promise<void>

      updateState(updates: Partial<ProcessModule<T>>): void

      add?(key: string, index?: number): Promise<void>

      /** 重命名 */
      rename(name: string): Promise<void>

      /** 获取操作状态 */
      getActionState?(action: TabActionType): TabActionState
      /** 执行保存操作 */
      save?(): void | Promise<boolean | void>
      /** 执行运行操作 */
      run?(): void | Promise<void>
      /** 执行调试操作 */
      debug?(): void | Promise<void>
      /** 执行编组操作 */
      group?(id: string | string[]): void | Promise<void>
      /** 执行解组操作 */
      ungroup?(id: string | string[]): void
      /** 切换多选状态 */
      toggleMultiSelect?(value?: boolean): void | Promise<void>
      /** 执行自定义操作 */
      executeAction?(action: TabActionType, params?: any): void | Promise<void>

      /** Tab 激活时调用 */
      onActivate?(): void | Promise<void>
      /** Tab 失活时调用 */
      onDeactivate?(): void | Promise<void>
      /** Tab 关闭前调用，返回 false 可阻止关闭 */
      onBeforeClose?(): boolean | Promise<boolean>
      /** Tab 关闭时调用 */
      onClose?(): void | Promise<void>
    }
  }
}
