const DEFAULT_PORT = 13159
const DEFAULT_HOST = import.meta.env.VITE_ASSISTANT_SERVICE_HOST
  ?? import.meta.env.VITE_SERVICE_HOST
  ?? 'localhost'
const DEFAULT_OPENCLAW_GATEWAY_PORT = 19878

function getStoredRoutePort() {
  const raw = window.localStorage.getItem('route_port')
  const port = Number(raw)
  return Number.isFinite(port) && port > 0 ? port : DEFAULT_PORT
}

export function getBaseURL() {
  const explicit = import.meta.env.VITE_ASSISTANT_API_BASE_URL?.trim()
  if (explicit)
    return explicit.replace(/\/$/, '')

  return `http://${DEFAULT_HOST}:${getStoredRoutePort()}`
}

export function getOpenClawManagerBaseUrl() {
  return `${getBaseURL()}/openclaw`
}

export function getOpenClawProxyWsUrl() {
  const explicit = import.meta.env.VITE_ASSISTANT_OPENCLAW_WS_URL?.trim()
  if (explicit)
    return explicit

  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${window.location.host}/openclaw`
}

export function getDirectOpenClawGatewayWsUrl() {
  const explicit = import.meta.env.VITE_ASSISTANT_OPENCLAW_GATEWAY_WS_URL?.trim()
  if (explicit)
    return explicit

  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://localhost:${DEFAULT_OPENCLAW_GATEWAY_PORT}`
}

interface ApiEnvelope<T> {
  code?: number | string
  data: T
  message?: string
  msg?: string
}

export async function requestJson<T>(path: string, init?: RequestInit, acceptedCodes: Array<number | string> = [200, '0000']) {
  const response = await fetch(`${getBaseURL()}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  })

  const payload = await response.json() as ApiEnvelope<T>

  if (!response.ok)
    throw new Error(payload?.message || payload?.msg || `Request failed (${response.status})`)

  if (acceptedCodes.length > 0 && payload.code != null && !acceptedCodes.includes(payload.code))
    throw new Error(payload.message || payload.msg || 'Request failed')

  return payload.data
}

export async function requestBlob(path: string, init?: RequestInit) {
  const response = await fetch(`${getBaseURL()}${path}`, init)
  if (!response.ok)
    throw new Error(`Request failed (${response.status})`)
  return await response.blob()
}
