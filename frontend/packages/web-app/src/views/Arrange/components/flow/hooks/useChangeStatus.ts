export function changeChecked(unCheckedIds: string[], checkedIds: string[]) {
  // const flowStore = useFlowStore()
  // const statusMap = new Map<string, boolean>()
  // unCheckedIds.forEach(id => statusMap.set(id, false))
  // checkedIds.forEach(id => statusMap.set(id, true))

  // flowStore.simpleFlowUIData.forEach((item, index) => {
  //   const checked = statusMap.get(item.id)
  //   if (checked !== undefined && item.checked !== checked) {
  //     const newItem = { ...item, checked }
  //     flowStore.setSimpleFlowUIDataByType(newItem, index, true)
  //   }
  // })
}

export function changeDebugging(id: string) {
  // const flowStore = useFlowStore()

  // const preDebugIndex = flowStore.simpleFlowUIData.findIndex(item => item.debugging)
  // if (preDebugIndex !== -1) {
  //   const preDebugItem = flowStore.simpleFlowUIData[preDebugIndex]
  //   const { debugging, ...newPreDebugItem } = preDebugItem
  //   flowStore.setSimpleFlowUIDataByType(newPreDebugItem, preDebugIndex, true)
  // }

  // if (!id)
  //   return

  // const curDebugIndex = flowStore.simpleFlowUIData.findIndex(item => item.id === id)
  // if (curDebugIndex !== -1) {
  //   const curDebugItem = flowStore.simpleFlowUIData[curDebugIndex]
  //   const newCurDebugItem = { ...curDebugItem, debugging: true }
  //   flowStore.setSimpleFlowUIDataByType(newCurDebugItem, curDebugIndex, true)
  // }
}
