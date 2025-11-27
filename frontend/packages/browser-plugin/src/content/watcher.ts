import { generateXPath, getElementBySelector, getElementsByXpath } from './element'

/**
 * Watches for changes to a DOM element based on provided selection criteria.
 *
 * Depending on the `checkType` and available selectors (`xpath`, `cssSelector`),
 * this function attempts to locate the target element using either XPath or CSS selectors,
 * optionally considering shadow DOM roots and position-only matching.
 *
 * - If `checkType` is `'customization'`, it prioritizes shadow root and selector-based matching.
 * - Otherwise, it generates an XPath from `pathDirs` and searches accordingly.
 *
 * @param data - Information describing the element to watch, including selectors, matching types, and shadow root context.
 * @returns An object describing the result of the search, including whether the element was found and details about the matching step.
 */
export function elementChangeWatcher(data: ElementInfo): WatchXPathResult {
  const { xpath, cssSelector, checkType, shadowRoot, matchTypes } = data
  const onlyPosition = matchTypes && matchTypes.includes('onlyPosition')
  let result: WatchXPathResult = {
    found: false,
    lastMatchedNode: null,
    lastMatchedStep: null,
    notFoundStep: null,
    notFoundIndex: 0,
  }
  if (checkType === 'customization') {
    if (shadowRoot) {
      return findNodeByCssSelectorStepwise(cssSelector, onlyPosition)
    }
    if (xpath) {
      return findNodeByXPathStepwise(xpath, onlyPosition)
    }
    if (cssSelector) {
      return findNodeByCssSelectorStepwise(cssSelector, onlyPosition)
    }
  }
  else {
    const dirXpath = generateXPath(data.pathDirs)
    result = findNodeByXPathStepwise(dirXpath, onlyPosition)
  }
  return result
}

/**
 * Attempts to locate a DOM node by progressively applying each step of a CSS selector.
 * Supports special `$shadow$` steps for traversing shadow DOM boundaries.
 *
 * @param selector - The CSS selector string, with steps separated by '>'.
 *                   Use `$shadow$` to indicate crossing into a shadow root.
 * @param onlyPosition - If true, restricts selection to positional matching (implementation-dependent).
 * @returns An object containing:
 *   - `found`: Whether the node was found.
 *   - `lastMatchedNode`: The last successfully matched DOM element, or `null`.
 *   - `lastMatchedStep`: The selector string up to the last matched step, or `null`.
 *   - `notFoundStep`: The selector string at which matching failed, or `null` if found.
 *   - `notFoundIndex`: The index (1-based) of the step at which matching failed, or `undefined` if found.
 */
function findNodeByCssSelectorStepwise(selector: string, onlyPosition: boolean = false): WatchXPathResult {
  const steps = selector
    .split('>')
    .map(s => s.trim())
    .filter(Boolean)

  let lastMatchedNode: Element | null = document.querySelector('html')
  let lastMatchedStep: string | null = null

  for (let i = 0; i < steps.length; i++) {
    let j = i + 1
    if (steps[i] === '$shadow$') {
      j = j + 1
      if (j > steps.length) {
        return {
          found: false,
          lastMatchedNode,
          lastMatchedStep,
          notFoundStep: selector,
          notFoundIndex: i + 1,
        }
      }
    }

    const partialSelector = steps.slice(0, j).join('>').trim()
    let nodes: Element[] | null = null

    try {
      nodes = getElementBySelector(partialSelector, onlyPosition)
    }
    catch {
      return {
        found: false,
        lastMatchedNode,
        lastMatchedStep,
        notFoundStep: partialSelector,
        notFoundIndex: i + 1,
      }
    }

    if (!nodes || nodes.length === 0) {
      return {
        found: false,
        lastMatchedNode,
        lastMatchedStep,
        notFoundStep: partialSelector,
        notFoundIndex: i + 1,
      }
    }

    lastMatchedNode = nodes[0] ?? null
    lastMatchedStep = partialSelector
  }

  return {
    found: true,
    lastMatchedNode,
    lastMatchedStep,
    notFoundStep: null,
  }
}

/**
 * Attempts to locate a DOM node by evaluating an XPath expression step by step.
 * At each step, the function tries to find the node corresponding to the current XPath segment.
 * If a segment fails to match, the function returns information about the last successfully matched node and step.
 *
 * @param xpath - The XPath expression to evaluate, split and processed stepwise.
 * @param onlyPosition - If true, restricts the search to positional matches (default: false).
 * @returns An object containing:
 *   - `found`: Whether the node was found for the full XPath.
 *   - `lastMatchedNode`: The last successfully matched DOM node, or `document` if none matched.
 *   - `lastMatchedStep`: The XPath string of the last successfully matched step, or `null` if none matched.
 *   - `notFoundStep`: The XPath string of the step that failed to match, or `null` if all matched.
 *   - `notFoundIndex`: The index (1-based) of the step that failed to match, or `undefined` if all matched.
 */
function findNodeByXPathStepwise(xpath: string, onlyPosition: boolean = false): WatchXPathResult {
  const steps = xpath.split('/').filter(s => s.trim() !== '')
  let lastMatchedNode: Node | null = document
  let lastMatchedStep: XPathStep | null = null
  let nextStep = ''

  for (let i = 0; i < steps.length; i++) {
    const step = i === 0 && !steps[i].startsWith('html') ? `//${steps[i]}` : `/${steps[i]}`
    nextStep = nextStep + step

    let eles: Node[] | null = null
    try {
      eles = getElementsByXpath(nextStep, onlyPosition)
    }
    catch {
      return {
        found: false,
        lastMatchedNode,
        lastMatchedStep,
        notFoundStep: nextStep,
        notFoundIndex: i + 1,
      }
    }

    const foundNode = eles && eles.length > 0 ? eles[0] : null
    if (!foundNode) {
      return {
        found: false,
        lastMatchedNode,
        lastMatchedStep,
        notFoundStep: nextStep,
        notFoundIndex: i + 1,
      }
    }

    lastMatchedNode = foundNode
    lastMatchedStep = nextStep
  }

  return {
    found: true,
    lastMatchedNode,
    lastMatchedStep,
    notFoundStep: null,
  }
}
