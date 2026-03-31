import { ref } from "vue";
import { createConfigParam, deleteConfigParam, getConfigParams, updateConfigParam } from '@/api/atom'

/**
 * 配置参数管理
 */
export class ConfigParameter implements RPA.Process.ConfigParameter {
  // 配置参数列表
  parameters = ref<RPA.ConfigParamData[]>([])
  // 类型：process | module
  private type: 'process' | 'module'

  constructor(public projectId: string, public id: string, type: 'process' | 'module' = 'process') {
    this.type = type
    this.init()
  }

  async init() {
    const params: any = {
      robotId: this.projectId,
    }
    if (this.type === 'process') {
      params.processId = this.id
    } else {
      params.moduleId = this.id
    }
    this.parameters.value = await getConfigParams(params)
  }

  // 生成唯一的配置参数名称
  private generateName() {
    const baseName = 'p_variable'
    let count = 0
    let variableName = baseName

    while (
      this.parameters.value.some(variable => variable.varName === variableName)
    ) {
      count += 1
      variableName = `${baseName}_${count}`
    }

    return variableName
  }

  // 添加参数
  async create() {
    const data: RPA.CreateConfigParamData = {
      varName: this.generateName(),
      varDirection: 0,
      varType: 'Str',
      varDescribe: '',
      varValue: '',
      robotId: this.projectId,
    }
    if (this.type === 'process') {
      data.processId = this.id
    } else {
      data.moduleId = this.id
    }
    const id = await createConfigParam(data)

    this.parameters.value.push({ id, ...data })
  }

  // 删除参数
  async delete(data: RPA.ConfigParamData) {
    await deleteConfigParam(data.id)
    this.parameters.value = this.parameters.value.filter(it => data.id !== it.id)
  }

  // 更新参数
  async update(data: RPA.ConfigParamData) {
    const updateData: any = { ...data, robotId: this.projectId }
    if (this.type === 'process') {
      updateData.processId = this.id
    } else {
      updateData.moduleId = this.id
    }
    await updateConfigParam(updateData)

    this.parameters.value = this.parameters.value.map(item =>
      item.id === data.id ? { ...item, ...data } : item,
    )
  }
}