// Constants
const THIS_PREFIX = '$this.'
const FORM_MAP_KEY = '$formMap'

type Scope = Record<string, unknown>

/**
 * Wraps code in a try-catch block and executes it with the provided scope
 */
function wrapCode(code: string, scope: Scope): unknown {
  const keys = Object.keys(scope)
  const values = Object.values(scope)

  const wrappedCode = `
    try {
      const $this = ${FORM_MAP_KEY};
      ${code}
    } catch (error) {
      console.error('Expression execution error:', error);
      return undefined;
    }
  `

  // eslint-disable-next-line no-new-func
  return new Function(...keys, wrappedCode).bind(null)(...values)
}

/**
 * Executes code in a sandboxed environment with restricted scope access
 */
export function sandbox(source: string, scope: Scope = {}): unknown {
  const whiteList: string[] = []
  const code = source.trim()

  const scopeProxy = new Proxy(scope, {
    has: (target, prop) => {
      const propStr = String(prop)
      if (whiteList.includes(propStr)) {
        return true
      }
      if (!Object.prototype.hasOwnProperty.call(target, prop)) {
        throw new Error(`Invalid expression - ${propStr}! You can not do that!`)
      }
      return true
    },
    get: (target, prop) => {
      const propStr = String(prop)
      if (whiteList.includes(propStr)) {
        return (window as unknown as Record<string, unknown>)[propStr]
      }
      return target[prop as keyof typeof target]
    },
  })

  return wrapCode(code, scopeProxy)
}

/**
 * 计算条件表达式
 * @param code 条件表达式
 * @param formValues 表单值
 * @returns 
 */
export function caculateConditional(code: string, formValues: Record<string, RPA.AtomDisplayItem>) {
  return sandbox(code, { [FORM_MAP_KEY]: formValues })
}

/**
 * 计算结果key
 * @param key 结果key
 * @returns 
 */
export function caculateResultKey(key: string): string {
  return key.startsWith(THIS_PREFIX) ? key.replace(THIS_PREFIX, '') : key
}
