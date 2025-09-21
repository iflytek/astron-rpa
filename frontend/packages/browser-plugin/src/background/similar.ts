/**
 * 根据 元素信息确定元素是否相似,相似及返回相似元素信息
 */
export function getSimilarElement(preElementInfo: ElementInfo, currentElementInfo: ElementInfo) {
  if (!isSimilarElement(preElementInfo, currentElementInfo)) {
    return false
  }
  const xpath = generateSimilarXapth(preElementInfo.xpath, currentElementInfo.xpath)

  const cssSelector = generateSimilarSelector(preElementInfo.cssSelector, currentElementInfo.cssSelector)

  const pathDirs = generateSimilarPathDirs(preElementInfo.pathDirs, currentElementInfo.pathDirs)

  // 对 currentElementInfo 的属性进行遍历，如果属性值和 preElementInfo 的属性值相同，则保持不变，否则设置为 preElementInfo 的属性值
  const similarElementInfo = { ...preElementInfo, xpath, cssSelector, pathDirs }
  return similarElementInfo
}
/**
 * 判断两个元素是否相似
 */
export function isSimilarElement(preElementInfo: ElementInfo, currentElementInfo: ElementInfo) {
  const { xpath, cssSelector, pathDirs } = preElementInfo
  const { xpath: currentXpath, cssSelector: currentCssSelector, pathDirs: currentPathDirs } = currentElementInfo
  const xpathArr = xpath.split('/')
  const currentXpathArr = currentXpath.split('/')
  const cssSelectorArr = cssSelector.split('>')
  const currentCssSelectorArr = currentCssSelector.split('>')

  // 存在以下情况，则认为两个元素不是相似元素
  if (preElementInfo.url !== currentElementInfo.url) {
    return false
  }
  if (xpathArr.length !== currentXpathArr.length) {
    return false
  }
  // 若存在 tag 不一样，但是路径长度一样，则认为两个元素不是相似元素
  if (xpathArr.length === currentXpathArr.length) {
    for (let i = 0; i < xpathArr.length; i++) {
      const leftTag = xpathArr[i]?.split('[')[0]
      const rightTag = currentXpathArr[i]?.split('[')[0]
      if (leftTag !== rightTag && leftTag !== '*' && rightTag !== '*') {
        return false
      }
    }
  }

  if (cssSelectorArr.length !== currentCssSelectorArr.length) {
    return false
  }
  // pathDirs 长度不一样，则认为两个元素不是相似元素
  if (pathDirs.length !== currentPathDirs.length) {
    return false
  }

  return true
}
/**
 * 得到相似的xpath，这里不在校验是否是相似元素
 */
export function generateSimilarXapth(preXpath: string, currentXpath: string) {
  if (preXpath === currentXpath) {
    return preXpath
  }
  const preXpathArr = preXpath.split('/')
  const currentXpathArr = currentXpath.split('/')
  for (let i = 0; i < preXpathArr.length; i++) {
    if (preXpathArr[i] !== currentXpathArr[i]) {
      preXpathArr[i] = preXpathArr[i]?.split('[')[0]
    }
  }
  const xpath = preXpathArr.join('/')
  return xpath
}

/**
 * 得到相似的selector，这里不在校验是否是相似元素
 */
export function generateSimilarSelector(preSelector: string, currentSelector: string) {
  if (preSelector === currentSelector) {
    return preSelector
  }
  const preSelectorArr = preSelector.split('>')
  const currentSelectorArr = currentSelector.split('>')
  for (let i = 0; i < preSelectorArr.length; i++) {
    // nth-child
    if (preSelectorArr[i] !== currentSelectorArr[i] && preSelectorArr[i].includes(':nth-child')) {
      preSelectorArr[i] = preSelectorArr[i].split(':nth-child')[0]
    }
    // class
    if (preSelectorArr[i] !== currentSelectorArr[i] && preSelectorArr[i].includes('.')) {
      preSelectorArr[i] = preSelectorArr[i].split('.')[0]
    }
    // id #
    if (preSelectorArr[i] !== currentSelectorArr[i] && preSelectorArr[i].includes('#')) {
      preSelectorArr[i] = preSelectorArr[i].split('#')[0]
    }
  }
  const selector = preSelectorArr.join('>')
  return selector
}

export function generateSimilarPathDirs(prePathDirs: Array<ElementDirectory>, currentPathDirs: Array<ElementDirectory>) {
  // 逆向遍历 prePathDirs
  for (let i = prePathDirs.length - 1; i >= 0; i--) {
    const prePathDir = prePathDirs[i]
    const currentPathDir = currentPathDirs[i]
    prePathDir.attrs.forEach((attr) => {
      attr.checked = false
      const currentAttr = currentPathDir.attrs.find(item => item.name === attr.name)
      if (!currentAttr) {
        attr.value = ''
      }
      if (currentAttr && currentAttr.name === 'id' && attr.value === currentAttr.value && attr.value !== '') {
        attr.checked = true
      }
      if (currentAttr && currentAttr.name === 'index' && attr.value !== '' && String(attr.value) === String(currentAttr.value)) {
        attr.checked = true
      }
      if (currentAttr && currentAttr.name === 'innertext') {
        attr.checked = false
        attr.value = ''
      }
    })
    const idChecked = prePathDir.attrs.some(item => item.name === 'id' && item.checked)
    if (idChecked) { // 存在id  则其他属性都为false
      prePathDir.attrs.forEach((attr) => {
        if (attr.name !== 'id') {
          attr.checked = false
        }
      })
    }
  }
  return prePathDirs
}

export function isSameIdStart(prePathDirs: Array<ElementDirectory>, currentPathDirs: Array<ElementDirectory>) {
  if (!prePathDirs || !currentPathDirs) {
    return false
  }
  if (prePathDirs.length === 0 || currentPathDirs.length === 0) {
    return false
  }
  const preFirst = prePathDirs[0]
  const currentFirst = currentPathDirs[0]
  const preIdAttr = preFirst.attrs.find(item => item.name === 'id' && item.checked && item.value !== '')
  const currentIdAttr = currentFirst.attrs.find(item => item.name === 'id' && item.checked && item.value !== '')
  if (preIdAttr && currentIdAttr) {
    return preIdAttr.value === currentIdAttr.value
  }
  else {
    return false
  }
}
