/** @format */

import { useFlowStore } from '@/stores/useFlowStore'
import { Group, GroupEnd } from '@/views/Arrange/config/atomKeyMap'
import { generateGroupName, generateId, generateVarName, getAllGlobalVariable, getFlowVariable } from '@/views/Arrange/utils/generateData'

// 修改粘贴的原子能力的基础字段，包括id，分组名称、嵌套类关联Id
export function changePasteAtoms(arr) {
  const idMap = {} // 保存旧id和新的id的map
  const groupName = []
  arr.forEach((atom) => {
    // 修改id
    const newId = generateId(atom.key)
    idMap[atom.id] = newId
    // 修改分组名称
    if (atom.key === Group) {
      const gname = generateGroupName()
      atom.alias = gname
      groupName.push(gname)
    }
    if (atom.key === GroupEnd) {
      atom.alias = groupName.pop()
    }
    atom.id = newId
  })
  useFlowStore().generateContactMap(arr)
  // arr.forEach((atom) => {
  //   // 修改分组名称
  //   if (atom.key === GroupEnd)
  //     changeAnotherName(atom, groupNameMap[atom.relationStartId])
  //   // 修改嵌套类原子能力的关联节点
  //   if (atom.relationStartId)
  //     atom.relationStartId = idMap[atom.relationStartId]
  //   if (atom.relationEndId)
  //     atom.relationEndId = idMap[atom.relationEndId]
  // })
}

// 跨工程粘贴，要删除全局变量
export function delPasteGlobalVar(arr) {
  console.log('arr', arr)
}

// 修改粘贴的原子能力的流变量
export function changePasteAtomFlowVar(arr) {
  const varMap = {} // 保存旧变量名和新的变量名的map
  const allFlowVariable = getFlowVariable()
  const allGlobalVariable = getAllGlobalVariable()
  // 生成新的输出变量
  arr.forEach((atom) => {
    atom.outputList.forEach((outItem) => {
      if (outItem.value.length === 1) {
        if (allGlobalVariable.includes(outItem.value[0].value))
          return
        const newVarName = generateVarName(outItem.key, allFlowVariable)
        varMap[outItem.value[0].value] = newVarName
        outItem.value[0].value = newVarName
      }
    })
  })

  // 修改原子能力输入变量为新生成的输出变量
  arr.forEach((atom) => {
    atom.inputList.forEach((inputItem: any) => {
      if (Array.isArray(inputItem.value)) {
        inputItem.value.forEach((v) => {
          if (varMap[v.value]) {
            v.value = varMap[v.value]
          }
        })
      }
    })
  })
}

export function generatePasteAtoms(clipBoardAtoms) {
  // 修改粘贴的原子能力的基础字段，包括id，分组名称、嵌套类关联Id
  changePasteAtoms(clipBoardAtoms)
  // TODO: 跨工程复制粘贴，删除全局变量
  // delPasteGlobalVar(clipBoardAtoms)
  // 修改粘贴的原子能力流变量
  changePasteAtomFlowVar(clipBoardAtoms)
  return clipBoardAtoms
}
