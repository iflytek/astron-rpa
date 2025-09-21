function extractDependencies(code: string): string[] {
  const noStrings = code.replace(/'[^']*'|"[^"]*"/g, '')
  const noComments = noStrings.replace(/\/\/.*|\/\*[\s\S]*?\*\//g, '')
  const matches = noComments.match(/\$this\.[a-zA-Z_$][\w$]*(\.[a-zA-Z_$][\w$]*)*/g) || []

  const allPaths = matches.map((match) => {
    const parts = match.split('.')
    parts.shift()
    return parts
  })

  const dependencies = new Set<string>()
  allPaths.forEach((parts) => {
    if (parts.length > 0) {
      dependencies.add(parts[0])
    }
  })

  return Array.from(dependencies)
}

// const getNestedValue = (obj: any, path: string) => {
//     const parts = path.split('.')
//     let current = obj
//     for (const part of parts) {
//         if (current === null || current === undefined) {
//             return undefined
//         }
//         current = current[part]
//     }
//     return current
// }

function setNestedValue(obj: any, path: string, value: any) {
  const parts = path.split('.')
  let current = obj
  for (let i = 0; i < parts.length - 1; i++) {
    const part = parts[i]
    if (!(part in current)) {
      current[part] = {}
    }
    current = current[part]
  }
  current[parts[parts.length - 1]] = value
}

function buildFormMap(lists: any[]): { [key: string]: any } {
  const formMap: { [key: string]: any } = {}
  lists.forEach((list) => {
    if (Array.isArray(list)) {
      list.forEach((item) => {
        if (item.key) {
          formMap[item.key] = item
        }
      })
    }
  })
  return formMap
}

function withedCode(code: string, scope: any) {
  const keys = Object.keys(scope)
  const values = Object.values(scope)

  const wrappedCode = `
    try {
      const $this = $formMap;
      ${code}
    } catch (error) {
      console.error('Expression execution error:', error)
      return undefined
    }
  `
  // eslint-disable-next-line no-new-func
  return new Function(...keys, wrappedCode).bind(null)(...values)
}

export function sandbox(source: string, scope = {}) {
  const whiteList = []
  const code = source.trim()

  const scopeProxy = new Proxy(scope, {
    has: (target, prop) => {
      const propStr = String(prop)
      if (whiteList.includes(propStr)) {
        return true
      }
      if (!Object.prototype.hasOwnProperty.call(target, prop)) {
        throw new Error(`Invalid expression - ${String(prop)}! You can not do that!`)
      }
      return true
    },
    get: (target, prop) => {
      const propStr = String(prop)
      if (whiteList.includes(propStr)) {
        return (window as any)[propStr]
      }
      return target[prop]
    },
  })

  return withedCode(code, scopeProxy)
}

export function executeExpression(expression: string, targetProp: string, allLists: any[]) {
  const formMap = buildFormMap(allLists)
  const fullPath = targetProp.replace('$this.', '')
  const [targetObj, ...restPath] = fullPath.split('.')

  const result = sandbox(expression, { $formMap: formMap })

  if (formMap[targetObj]) {
    if (restPath.length > 0) {
      setNestedValue(formMap[targetObj], restPath.join('.'), result)
    }
    else {
      formMap[targetObj][targetObj] = result
    }
  }

  return result
}

export function checkAndExecuteDependencies(changedKey: string, allLists: any[], getDependencyMap: () => Map<string, Array<{ expression: string, targetItem: any, targetProp: string }>>) {
  const dependencyMap = getDependencyMap()
  const dependentExpressions = dependencyMap.get(changedKey) || []

  dependentExpressions.forEach(({ expression, targetProp }) => {
    executeExpression(expression, targetProp, allLists)
  })
}

export function buildDependencyMap(lists: any[]): Map<string, Array<{ expression: string, targetItem: any, targetProp: string }>> {
  const dependencyMap = new Map<string, Array<{ expression: string, targetItem: any, targetProp: string }>>()

  Object.values(lists).forEach((list) => {
    if (!Array.isArray(list))
      return
    list.forEach((item) => {
      if (item.dynamics?.length) {
        item.dynamics.forEach((condition: any) => {
          if (condition.expression) {
            const deps = extractDependencies(condition.expression)
            deps.forEach((dep) => {
              const expressions = dependencyMap.get(dep) || []
              expressions.push({
                expression: condition.expression,
                targetItem: item,
                targetProp: condition.key,
              })
              dependencyMap.set(dep, expressions)
            })
          }
        })
      }
    })
  })

  return dependencyMap
}

export function initializeExpressions(allLists: any[], dependencyMap: Map<string, Array<{ expression: string, targetItem: any, targetProp: string }>>) {
  const allExpressions = new Set<{ expression: string, targetItem: any, targetProp: string }>()
  dependencyMap.forEach((expressions) => {
    expressions.forEach((exp) => {
      allExpressions.add(exp)
    })
  })

  allExpressions.forEach(({ expression, targetProp }) => {
    executeExpression(expression, targetProp, allLists)
  })
}

export function caculateConditional(dynamics: RPA.AtomFormItemConditional[], formList: Record<string, unknown>, sourceForm: Record<string, unknown>): boolean {
  const flagArr = dynamics.map((item) => {
    const { expression, key } = item
    const fullPath = key.replace('$this.', '')
    const [targetObj, ...restPath] = fullPath.split('.')
    const result = sandbox(expression, { $formMap: formList })
    if (sourceForm.key === targetObj) {
      if (restPath.length > 0) {
        setNestedValue(sourceForm, restPath.join('.'), result)
      }
      else {
        sourceForm[targetObj] = result
      }
    }
    return result
  })
  return flagArr.every(i => i)
}
