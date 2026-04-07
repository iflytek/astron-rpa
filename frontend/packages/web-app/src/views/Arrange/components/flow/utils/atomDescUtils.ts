
// 展示
export function getValue(value = []) {
  return value.map(i => i.value).join('')
}

export function setStyle() {
  const timer = setTimeout(() => {
    clearTimeout(timer)
    let elements = document.getElementsByClassName('tags-suffix')
    if (elements && elements.length > 0 && elements[0].children.length === 2) {
      const elementFirst = elements[0] as HTMLElement
      elementFirst.style.setProperty('width', '40px', 'important')
      let inputEditor = document.getElementsByClassName('rpa-wangEditor')[0]
      if (inputEditor) {
        inputEditor[0].style.setProperty('margin-right', '38px', 'important')
      }
      inputEditor = null
    }
    elements = null
  }, 0)
}

export function validateConditional({ operands, operators }, formObj) {
  const operandsResults = operands.map((item) => {
    const leftValue = formObj[item.left].value
    const rightValue = item.right
    let result = false
    try {
      switch (item.operator) {
        case '>':
          result = leftValue > rightValue
          break
        case '<':
          result = leftValue < rightValue
          break
        case '==':
          result = leftValue === rightValue
          break
        case '>=':
          result = leftValue >= rightValue
          break
        case '<=':
          result = leftValue <= rightValue
          break
        case '!=':
          result = leftValue !== rightValue
          break
        case 'in':
          result = rightValue.includes(leftValue)
          break
        default:
      }
    }
    catch {
      result = false
    }
    return result
  })

  // operators==='and' 条件全部满足，则此项展示, operators==='or' 条件部分满足，
  return operators === 'and' ? operandsResults.every(i => i) : operandsResults.some(i => i)
}
