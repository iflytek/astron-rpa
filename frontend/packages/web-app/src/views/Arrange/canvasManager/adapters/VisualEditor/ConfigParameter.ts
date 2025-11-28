import { ref } from "vue";
import { createConfigParam, deleteConfigParam, getConfigParams, updateConfigParam } from '@/api/atom'

/**
 * 配置参数管理
 */
export class ConfigParameter implements RPA.Process.ConfigParameter {
  // 配置参数列表
  parameters = ref<RPA.ConfigParamData[]>([])

  constructor(public projectId: string, public processId: string) {
    this.init()
  }

  async init() {
    this.parameters.value = await getConfigParams({
      robotId: this.projectId,
      processId: this.processId,
    })
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
      processId: this.processId,
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
    await updateConfigParam({ ...data, robotId: this.processId })

    this.parameters.value = this.parameters.value.map(item =>
      item.id === data.id ? { ...item, ...data } : item,
    )
  }
}