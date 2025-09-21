export interface HeaderValues {
  token?: string
  etag?: string
}

export async function endpointGet(
  endpoint: string,
  headerValues: HeaderValues,
  body?: string | FormData,
  contentType = 'application/json',
) {
  return fetch(endpoint, {
    method: 'GET',
    headers: makeHeaders(headerValues, contentType),
    body,
  })
}

export async function endpointPost(
  endpoint: string,
  headerValues: HeaderValues,
  body?: string | FormData,
  contentType = 'application/json',
) {
  return fetch(endpoint, {
    method: 'POST',
    headers: makeHeaders(headerValues, contentType),
    body,
  })
}

export async function endpointPut(
  endpoint: string,
  headerValues: HeaderValues,
  body?: string | FormData,
  contentType = 'application/json',
) {
  return fetch(endpoint, {
    method: 'PUT',
    headers: makeHeaders(headerValues, contentType),
    body,
  })
}

export async function endpointDelete(
  endpoint: string,
  headerValues: HeaderValues,
  body?: string | FormData | Blob,
  contentType = 'application/json',
) {
  return fetch(endpoint, {
    method: 'DELETE',
    headers: makeHeaders(headerValues, contentType),
    body,
  })
}

function makeHeaders(_headerValues: HeaderValues, contentType = 'application/json') {
  const headers: Record<string, string> = {}

  if (contentType) {
    headers['Content-Type'] = contentType
  }

  return headers
}
