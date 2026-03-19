import { connectOpenClawGateway } from './openclaw'
import { getDirectOpenClawGatewayWsUrl, getOpenClawProxyWsUrl } from './runtime'

const OPENCLAW_HEALTH_REQUEST_TIMEOUT_MS = 5000

function getDefaultProbeWsUrls() {
  const directUrl = getDirectOpenClawGatewayWsUrl()
  const proxyUrl = getOpenClawProxyWsUrl()

  if ((window as any)?.electron)
    return [directUrl, proxyUrl]

  if (window.location.protocol === 'rpa:' || window.location.protocol === 'file:')
    return [directUrl, proxyUrl]

  return [proxyUrl, directUrl]
}

export async function probeOpenClawReadiness(params?: {
  token?: string
  wsUrl?: string
  connectTimeoutMs?: number
  requestTimeoutMs?: number
}) {
  const candidateUrls = params?.wsUrl
    ? [params.wsUrl]
    : getDefaultProbeWsUrls()
  let lastError: unknown

  for (const wsUrl of candidateUrls) {
    const connection = await connectOpenClawGateway({
      token: params?.token,
      wsUrl,
      connectTimeoutMs: params?.connectTimeoutMs,
    }).catch((error) => {
      lastError = error
      return null
    })

    if (!connection)
      continue

    try {
      await connection.request(
        'health',
        { probe: true },
        params?.requestTimeoutMs ?? OPENCLAW_HEALTH_REQUEST_TIMEOUT_MS,
      )
      return
    }
    catch (error) {
      lastError = error
    }
    finally {
      connection.close()
    }
  }

  throw lastError instanceof Error
    ? lastError
    : new Error('Unable to connect to openclaw gateway.')
}
