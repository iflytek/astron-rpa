/* eslint-disable */
self.addEventListener('message', (event) => {
  const { data } = event;
  workerhandler(data.key, data.params);
});

const funcMap = {
  flowDataElementUpdate,
  elementUsedInFlow,
}

function workerhandler(key: string, params: any) {
  funcMap[key](params);
}

function flowDataElementUpdate(params: { currentFlowData: any, element: any, type: string }) {
  console.log('params: ', params);
  const { currentFlowData, element, type } = params;
  const userNodes = JSON.parse(currentFlowData)
  const changeItem = []
  Object.keys(userNodes).forEach(curItem => {
    userNodes[curItem].forEach((item, i) => {
      const nextAtom = item
      if (isArray(nextAtom.inputList)) {
        nextAtom.inputList.forEach((inputItem) => {
          if (isArray(inputItem.value)) {
            if (type === 'rename') {
              const eleItem = findItem(inputItem.value, 'element', element.elementId)
              if (eleItem) {
                eleItem.value = element.name
                changeItem.push({
                  index: i,
                  node: nextAtom,
                  process: curItem
                })
              }
            }
            if (type === 'delete') {
              const eleItemIndex = findItemIndex(inputItem.value, 'element', element.elementIds)
              if (eleItemIndex !== -1) {
                inputItem.value.splice(eleItemIndex, 1)
                changeItem.push({
                  index: i,
                  node: nextAtom,
                  process: curItem
                })
              }
            }
          }
        })
      }
    })
  })
  self.postMessage({
    key: 'flowDataElementUpdate',
    params: changeItem,
  }, {
    targetOrigin: location.origin,
  })
}

function elementUsedInFlow(params: { currentFlowData: any[] }) {
  const { currentFlowData } = params;
  const unusedElementsIdSet = new Set(); // 存储未使用的元素id, 重复的id只存储一次
  currentFlowData.forEach((item) => {
    if (isArray(item.inputList)) {
      item.inputList.forEach((inputItem) => {
        if (isArray(inputItem.value)) {
          inputItem.value.forEach((valueItem) => {
            if (valueItem.type === 'element') {
              unusedElementsIdSet.add(valueItem.data)
            }
          })
        }
      })
    }
  })

  self.postMessage({
    key: 'elementUsedInFlow',
    params: {
      usedElementsIds: Array.from(unusedElementsIdSet)
    }
  }, {
    targetOrigin: location.origin,
  })
}


function findItem(arr: any[], type: string, id: string) {
  return arr.find((item) => item.type === type && item.data === id)
}

function findItemIndex(arr: any[], type: string, ids: string[]) {
  return arr.findIndex((item) => item.type === type && ids.includes(item.data))
}
function isArray(arr: any) {
  return arr && Array.isArray(arr)
}
