export function getQuery() {
  const href = window.location.href
  const queryStr = href.split('?')[1] || ''
  return Object.fromEntries(new URLSearchParams(queryStr))
}
