import { ref } from 'vue'
import { cloneDeep, isEmpty } from 'lodash-es'

import { ATOM_KEY_MAP } from '@/constants/atom'
import { BASE_FORM } from '@/views/Arrange/config/atom'

import type { VisualEditor } from '.'

class NodeParameter implements RPA.Process.NodeParameter {
  /** 当前激活的原子能力ID */
  public activeAtomId = ref<string>()
  /** 当前激活的实例 */
  public activeInstance: VisualEditor | null = null

  /** 表单配置 */
  public formTabs = ref<RPA.Process.AtomTabs[]>([])

  get activeAtom() {
    if (!this.activeInstance || !this.activeAtomId.value) return null

    return this.activeInstance.state.data.find(it => it.id === this.activeAtomId.value) || null
  }

  /**
   * 检查表单项是否违反了必填规则
   * @param item 表单项数据
   * @returns true 表示必填项为空（违反规则），false 表示已填写或非必填
   */
  private validateRequired(formItem: RPA.AtomDisplayItem): boolean {
    const { required, value: atomValue } = formItem

    // 如果不是必填项，直接返回 false
    if (!required) {
      return false
    }

    // 数组类型：检查是否所有元素都为空
    if (Array.isArray(atomValue)) {
      const allEmpty = atomValue.every(atomItem => Object.is(atomItem.value, ''))
      return allEmpty
    }

    // 布尔类型：布尔值始终视为已填写
    if (typeof atomValue === 'boolean') {
      return false
    }

    // 字符串类型：空字符串表示未填写
    if (atomValue === '') {
      return true
    }

    // 其他类型：视为已填写
    return false
  }

  /**
   * 检查表单项是否符合长度限制
   * @param item 表单项数据
   * @returns true 表示符合长度限制，false 表示违反长度限制
   */
  private validateLimitLength(formItem: RPA.AtomDisplayItem): boolean {
    const { limitLength, value } = formItem

    // 如果没有长度限制配置，直接返回 true
    if (!limitLength || limitLength.length !== 2) {
      return true
    }

    // TODO: 还不清楚这里的 getRealValue 是做什么的
    // const atomValue = getRealValue(value)
    const atomValue = value

    // 如果值不是字符串或数组类型（没有 length 属性），无法进行长度检查
    if (typeof atomValue !== 'string' && !Array.isArray(atomValue)) {
      return true
    }

    const [min, max] = limitLength
    const valueLength = atomValue.length

    // 将字符串 '-1' 转换为数字 -1，统一处理
    const minLimit = min === '-1' ? -1 : Number(min)
    const maxLimit = max === '-1' ? -1 : Number(max)

    // [-1, 16] 有最大长度限制
    if (minLimit === -1) {
      return valueLength <= maxLimit
    }

    // [4, -1] 有最小长度限制
    if (maxLimit === -1) {
      return valueLength >= minLimit
    }

    // [4, 16] 有最小最大长度限制
    return valueLength >= minLimit && valueLength <= maxLimit
  }

  // 对表单项进行必填及其他校验
  public validateFormItems(formItem: RPA.AtomDisplayItem): string[] {
    const errors = [];
    
    const required = this.validateRequired(formItem)
    if (required) {
      errors.push(`${formItem.title}必填`)
    }

    const limitLength = this.validateLimitLength(formItem)
    if (!limitLength) {
      const [min, max] = formItem.limitLength
      // 统一将字符串 '-1' 转换为数字 -1 处理
      const minLimit = min === '-1' ? -1 : Number(min)
      const maxLimit = max === '-1' ? -1 : Number(max)
      
      let tip: string
      if (minLimit === -1) {
        // 只有最大长度限制
        tip = `不应大于${maxLimit}`
      } else if (maxLimit === -1) {
        // 只有最小长度限制
        tip = `不应小于${minLimit}`
      } else {
        // 有最小和最大长度限制
        tip = `应在${minLimit}到${maxLimit}之间`
      }
      errors.push(`${formItem.title}长度${tip}`)
    }

    return errors
  }

  /**
   * 切换当前激活的原子能力
   * @param id 原子能力ID
   */
  toggleAtomActive(instance: VisualEditor, id: string) {
    this.activeInstance = instance
    this.activeAtomId.value = id

    console.log('切换激活原子能力:', id, instance)
    
    this.generateFormTabs(id)
  }

  // 生成基础信息表单
  private generateBaseItems(initData: RPA.Atom): RPA.AtomFormBaseForm[] {
    const baseItems = cloneDeep(BASE_FORM)

    return baseItems.map((i) => {
      const isGroup = initData.key === ATOM_KEY_MAP.Group

      if (i.key === 'baseName') {
        i.value = initData.title
        i.title = isGroup ? '分组名称' : i.title
      } else if (i.key === 'anotherName') {
        i.value = initData.alias ?? initData.title
        i.title = isGroup ? '分组别名' : i.title
      }
      
      return i
    })
  }
  
  /**
   * 生成表单配置
   * @param atom 原子能力
   * @returns 表单配置
   */
  private generateFormTabs(id: string): RPA.Process.AtomTabs[] {
    const atom = this.activeInstance.state.data.find(it => it.id === id)
    if (!atom) return []

    const { inputList = [], outputList = [], advanced = [], exception = [] } = atom

    const baseForm = this.generateBaseItems(atom)

    // 给表单项添加 sourceValue
    const setSourceValue = (formItems: RPA.AtomDisplayItem[], prefix: string) => {
      return formItems.map((item, index) => ({
        ...item,
        sourceValue: `${prefix}[${index}].value`,
      }))
    }
    
    // 基本参数表单配置
    const baseParam: RPA.Process.AtomTabs = {
      key: 'baseParam',
      name: 'basicParameters',
      params: [
        {
          name: { 'zh-CN': '基本信息', 'en-US': 'Base information' },
          key: `base-${atom.id}`,
          formItems: baseForm,
        },
        {
          name: { 'zh-CN': '输入信息', 'en-US': 'Input information' },
          key: `input-${atom.id}`,
          id: atom.id ?? '',
          atomKey: atom.key ?? '',
          formItems: setSourceValue(inputList, 'inputList'),
        },
        {
          name: { 'zh-CN': '输出信息', 'en-US': 'Output information' },
          key: `output-${atom.id}`,
          formItems: setSourceValue(outputList, 'outputList'),
        },
      ],
    }
    // 高级参数表单配置
    const advancedParam: RPA.Process.AtomTabs = {
      key: 'advancedParam',
      name: 'advancedParameters',
      params: [
        {
          key: `advanced-${atom.id}`,
          formItems: setSourceValue(advanced, 'advanced'),
        },
      ],
    }
    // 异常处理表单配置
    const exceptionParam: RPA.Process.AtomTabs = {
      key: 'exceptParam',
      name: 'exceptionHandling',
      params: [
        {
          key: `exception-${atom.id}`,
          formItems: setSourceValue(exception, 'exception'),
        },
      ],
    }

    let atomTabs: RPA.Process.AtomTabs[] = atom.noAdvanced ? [baseParam] : [baseParam, advancedParam, exceptionParam]

    // 先过滤 atomTabs 中的 formItems，formItems 为空，则删除该 param
    atomTabs = atomTabs.map(item => {
      item.params = item.params.filter(param => !isEmpty(param.formItems))
      return item
    })

    // 再过滤 atomTabs 中的 params，params 为空，则删除该 tab
    atomTabs = atomTabs.filter(item => !isEmpty(item.params))

    this.formTabs.value = atomTabs
  }

  /**
   * 更新表单项值
   * @param key 表单项key
   * @param value 表单项值
   */
  public updateValue = (key: string, value: any) => {
    const formItems = this.formTabs.value.flatMap(item => item.params).flatMap(item => item.formItems)

    const sourceKey = formItems.find(item => item.key === key)?.sourceValue
    if (!sourceKey) return

    this.activeInstance.updateFormItemValue(this.activeAtomId.value, sourceKey, value)

    // 重新生成表单配置
    this.generateFormTabs(this.activeAtomId.value)
  }
}

export const nodeParameter = new NodeParameter()
