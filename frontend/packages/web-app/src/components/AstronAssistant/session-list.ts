interface SessionListItem {
  id: string
  updatedAt: number
}

function sortSessionsByUpdatedAt<T extends SessionListItem>(sessions: T[]) {
  return [...sessions].sort((left, right) => right.updatedAt - left.updatedAt)
}

export function buildRecentSessionList<T extends SessionListItem>(
  sessions: T[],
  currentSessionId: string,
  limit: number,
): T[] {
  const sorted = sortSessionsByUpdatedAt(sessions)
  if (sorted.length <= limit)
    return sorted

  const currentIndex = sorted.findIndex(session => session.id === currentSessionId)
  if (currentIndex < 0 || currentIndex < limit)
    return sorted.slice(0, limit)

  return [...sorted.slice(0, limit - 1), sorted[currentIndex]]
}

export function resolveNextSessionIdAfterDelete<T extends SessionListItem>(
  sessions: T[],
  deletedSessionId: string,
  currentSessionId: string,
): string | null {
  const remaining = sortSessionsByUpdatedAt(
    sessions.filter(session => session.id !== deletedSessionId),
  )

  if (!remaining.length)
    return null

  if (currentSessionId !== deletedSessionId)
    return currentSessionId

  return remaining[0]?.id ?? null
}
