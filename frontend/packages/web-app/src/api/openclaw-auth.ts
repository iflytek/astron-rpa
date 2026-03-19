const OPENCLAW_MANUAL_TOKEN_KEY = 'astron.openclaw.manualGatewayToken.v1'

function getOpenClawStorage() {
  try {
    return window.localStorage
  }
  catch {
    return null
  }
}

export function getConfiguredOpenClawToken(explicitToken?: string) {
  return (
    explicitToken
    || import.meta.env.VITE_ASSISTANT_OPENCLAW_TOKEN
    || import.meta.env.VITE_OPENCLAW_TOKEN
    || undefined
  )
}

export function getStoredManualOpenClawToken() {
  const token = getOpenClawStorage()?.getItem(OPENCLAW_MANUAL_TOKEN_KEY)?.trim()
  return token || undefined
}

export function storeManualOpenClawToken(token: string) {
  const normalized = token.trim()
  if (!normalized) {
    clearStoredManualOpenClawToken()
    return
  }

  getOpenClawStorage()?.setItem(OPENCLAW_MANUAL_TOKEN_KEY, normalized)
}

export function clearStoredManualOpenClawToken() {
  getOpenClawStorage()?.removeItem(OPENCLAW_MANUAL_TOKEN_KEY)
}

export async function resolveOpenClawToken(explicitToken?: string) {
  const configuredToken = getConfiguredOpenClawToken(explicitToken)
  if (configuredToken)
    return configuredToken

  const tokenGetter = (window as any)?.electron?.openclaw?.getToken
  if (typeof tokenGetter !== 'function')
    return getStoredManualOpenClawToken()

  try {
    const electronToken = await tokenGetter()
    if (electronToken)
      return electronToken
  }
  catch (error) {
    console.warn('Failed to load OpenClaw token from Electron:', error)
  }

  return getStoredManualOpenClawToken()
}
