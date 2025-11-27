/**
 * Determine whether elements are similar based on the element information.
 * If they are similar, return the information of similar elements
 */
export function getSimilarElement(preElementInfo: ElementInfo, currentElementInfo: ElementInfo) {
  if (!isSimilarElement(preElementInfo, currentElementInfo)) {
    return false
  }
  const xpath = generateSimilarXapth(preElementInfo.xpath, currentElementInfo.xpath)

  const cssSelector = generateSimilarSelector(preElementInfo.cssSelector, currentElementInfo.cssSelector)

  const pathDirs = generateSimilarPathDirs(preElementInfo.pathDirs, currentElementInfo.pathDirs)

  const similarElementInfo = { ...preElementInfo, xpath, cssSelector, pathDirs }
  return similarElementInfo
}

/**
 * Determines whether two elements are considered similar based on their XPath, CSS selector, path directories, and URL.
 *
 * The function compares the following properties of the provided `ElementInfo` objects:
 * - `url`: Must be identical.
 * - `xpath`: Must have the same number of segments, and each segment's tag name must match (wildcards '*' are allowed).
 * - `cssSelector`: Must have the same number of segments.
 * - `pathDirs`: Must have the same length.
 *
 * @param preElementInfo - The reference element information.
 * @param currentElementInfo - The element information to compare against the reference.
 * @returns `true` if the elements are considered similar; otherwise, `false`.
 */
function isSimilarElement(preElementInfo: ElementInfo, currentElementInfo: ElementInfo) {
  const { cssSelector, pathDirs } = preElementInfo
  const { cssSelector: currentCssSelector, pathDirs: currentPathDirs } = currentElementInfo
  const cssSelectorArr = cssSelector.split('>')
  const currentCssSelectorArr = currentCssSelector.split('>')

  if (preElementInfo.url !== currentElementInfo.url) {
    return false
  }

  if (cssSelectorArr.length !== currentCssSelectorArr.length) {
    return false
  }

  if (pathDirs.length !== currentPathDirs.length) {
    return false
  }

  if (pathDirs.length === currentPathDirs.length) {
    for (let i = 0; i < pathDirs.length; i++) {
      if (pathDirs[i].tag !== currentPathDirs[i].tag) {
        return false
      }
    }
  }

  return true
}

/**
 * Generates a similar XPath by comparing two XPath strings and modifying the differing segments.
 * If the two XPaths are identical, returns the original XPath.
 * For each segment that differs, removes any index (e.g., `[1]`) from the segment in the first XPath.
 *
 * @param preXpath - The base XPath string to be modified.
 * @param currentXpath - The XPath string to compare against.
 * @returns A new XPath string with differing segments normalized (index removed).
 */
function generateSimilarXapth(preXpath: string, currentXpath: string) {
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
 * Generates a similar CSS selector by comparing a previous selector with a current selector.
 * If the selectors are identical, returns the previous selector.
 * Otherwise, iterates through each selector segment and removes specific attributes
 * (such as `:nth-child`, class names, and IDs) from segments that differ between the two selectors.
 *
 * @param preSelector - The previous CSS selector string.
 * @param currentSelector - The current CSS selector string to compare against.
 * @returns A CSS selector string that is similar to the previous selector, with differing attributes removed.
 */
function generateSimilarSelector(preSelector: string, currentSelector: string) {
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

/**
 * Compares two arrays of `ElementDirectory` objects (`prePathDirs` and `currentPathDirs`) and updates the attributes of `prePathDirs`
 * based on the corresponding attributes in `currentPathDirs`. For each attribute in `prePathDirs`, if a matching attribute is not found
 * in `currentPathDirs`, its value is cleared and its `checked` property is set to `false`. If a matching attribute is found, the function
 * compares their types and values, updating the `checked` property accordingly. Special handling is applied for attributes named 'innertext'
 * or 'text', which are always unchecked and cleared. The function returns the modified `prePathDirs` array.
 *
 * @param prePathDirs - The array of `ElementDirectory` objects to be updated.
 * @param currentPathDirs - The array of `ElementDirectory` objects used as the reference for comparison.
 * @returns The updated array of `ElementDirectory` objects (`prePathDirs`).
 */
function generateSimilarPathDirs(prePathDirs: Array<ElementDirectory>, currentPathDirs: Array<ElementDirectory>) {
  for (let i = prePathDirs.length - 1; i >= 0; i--) {
    const prePathDir = prePathDirs[i]
    const currentPathDir = currentPathDirs[i]
    prePathDir.attrs.forEach((attr) => {
      const currentAttr = currentPathDir.attrs.find(item => item.name === attr.name)
      if (!currentAttr) {
        attr.value = ''
        attr.checked = false
      }
      else {
        // handle value comparison and type
        const isSameType = currentAttr.type === attr.type
        const isSameValue = String(attr.value) === String(currentAttr.value) && attr.value !== ''
        // handle checked logic
        if (isSameValue && isSameType) {
          attr.checked = currentAttr.checked && attr.checked // both true to keep true
        }
        else {
          attr.checked = false
        }
        // special handling for text
        if (currentAttr.name === 'innertext' || currentAttr.name === 'text') {
          attr.checked = false
          attr.value = ''
        }
      }
    })
  }
  return prePathDirs
}

/**
 * Determines whether the first directory in two arrays of `ElementDirectory` objects
 * have the same checked and non-empty `id` attribute value.
 *
 * @param prePathDirs - The array of previous path directories to compare.
 * @param currentPathDirs - The array of current path directories to compare.
 * @returns `true` if both arrays are non-empty, and their first elements have a checked, non-empty `id` attribute with the same value; otherwise, `false`.
 */
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
  if (!preIdAttr && !currentIdAttr) {
    return true
  }
  return false
}
