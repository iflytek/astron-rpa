function contextmenuPreventDefault(e: MouseEvent) {
  // 阻止默认行为
  e.preventDefault()
  // 执行其他操作
  // ...
}

function ctrlPreventDefault(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey)) {
    e.preventDefault()
  }
}

function shortCutPreventDefault(e: KeyboardEvent) {
  const key = e.key?.toLowerCase() ?? ''
  const ctrlKeys = ['s', 'j', 'r', 'f', 'g', 'p', 'u', 'z']
  const fkeys = ['f5', 'f3', 'f7', 'f12']
  const otherKeys = ['tab']

  if (ctrlKeys.includes(key)) {
    ctrlPreventDefault(e)
  }
  if (fkeys.includes(key)) {
    e.preventDefault()
  }
  if (otherKeys.includes(key)) {
    e.preventDefault()
  }
}

document.addEventListener('contextmenu', contextmenuPreventDefault)
document.addEventListener('keydown', shortCutPreventDefault)
