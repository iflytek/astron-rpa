type FetchLike = (input: string, init?: RequestInit) => Promise<Response>

export async function isDevEngineReady(
  port: number,
  fetchImpl: FetchLike = fetch,
): Promise<boolean> {
  try {
    const response = await fetchImpl(`http://127.0.0.1:${port}/rpa-local-route/health`, {
      signal: AbortSignal.timeout(1500),
    })
    return response.ok
  }
  catch {
    return false
  }
}
