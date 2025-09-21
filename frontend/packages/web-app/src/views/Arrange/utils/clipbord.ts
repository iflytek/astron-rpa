export function setClipBoardData(projectId: string | number, atoms: any = null, type: string) {
  localStorage.setItem('clipBoardData', JSON.stringify({
    projectId,
    atoms,
    type,
  }))
}

export function getClipBoardData(callback) {
  const clipBoardData = JSON.parse(localStorage.getItem('clipBoardData') || '{}')
  callback(clipBoardData)
}

// 退出应用时，清空临时文件的数据
export function clearClipBoardData() {
  // 先清空文件
  localStorage.removeItem('clipBoardData')
}
