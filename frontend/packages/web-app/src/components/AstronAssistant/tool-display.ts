type ToolArgs = Record<string, unknown>

interface ToolDisplay {
  title: string
  summary?: string
  detailLines: string[]
}

const FALLBACK_DETAIL_KEYS = [
  'command',
  'path',
  'url',
  'targetUrl',
  'targetId',
  'ref',
  'element',
  'node',
  'nodeId',
  'id',
  'requestId',
  'to',
  'channelId',
  'guildId',
  'userId',
  'name',
  'query',
  'pattern',
  'messageId',
]

function asRecord(value: unknown): ToolArgs | undefined {
  return value && typeof value === 'object' ? value as ToolArgs : undefined
}

function normalizeToolName(name?: string): string {
  return (name ?? 'tool').trim()
}

function defaultTitle(name: string): string {
  const cleaned = name.replace(/_/g, ' ').trim()
  if (!cleaned)
    return 'Tool'

  return cleaned
    .split(/\s+/)
    .map((part) => {
      const first = part.at(0)?.toUpperCase() ?? ''
      return `${first}${part.slice(1)}`
    })
    .join(' ')
}

function shortenHomeInString(input: string): string {
  if (!input)
    return input

  return input
    .replace(/^\/Users\/[^/]+(\/|$)/, '~$1')
    .replace(/^\/home\/[^/]+(\/|$)/, '~$1')
    .replace(/^C:\\Users\\[^\\]+(\\|$)/i, '~$1')
}

function coerceDisplayValue(value: unknown, maxStringChars = 160): string | undefined {
  if (value == null)
    return undefined

  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed)
      return undefined
    const firstLine = trimmed.split(/\r?\n/)[0]?.trim() ?? ''
    if (!firstLine)
      return undefined
    if (firstLine.length > maxStringChars)
      return `${firstLine.slice(0, maxStringChars - 3)}...`
    return firstLine
  }

  if (typeof value === 'boolean' || typeof value === 'number')
    return String(value)

  if (Array.isArray(value)) {
    const parts = value
      .map(entry => coerceDisplayValue(entry, maxStringChars))
      .filter((entry): entry is string => Boolean(entry))
    if (!parts.length)
      return undefined
    return parts.slice(0, 3).join(', ')
  }

  return undefined
}

function lookupValueByPath(args: ToolArgs | undefined, path: string): unknown {
  if (!args)
    return undefined

  let current: unknown = args
  for (const segment of path.split('.')) {
    if (!segment || !current || typeof current !== 'object')
      return undefined
    current = (current as ToolArgs)[segment]
  }
  return current
}

function resolvePathArg(args: ToolArgs | undefined): string | undefined {
  if (!args)
    return undefined

  for (const candidate of [args.path, args.file_path, args.filePath, args.url]) {
    const value = coerceDisplayValue(candidate)
    if (value)
      return value
  }

  return undefined
}

function resolveWriteDetail(toolKey: string, args: ToolArgs | undefined): string | undefined {
  const path = resolvePathArg(args)
  if (!path)
    return undefined

  if (toolKey === 'attach')
    return `from ${shortenHomeInString(path)}`

  const destinationPrefix = toolKey === 'edit' ? 'in' : 'to'
  const content = coerceDisplayValue(args?.content, 400)
    ?? coerceDisplayValue(args?.newText, 400)
    ?? coerceDisplayValue(args?.new_string, 400)

  if (content)
    return `${destinationPrefix} ${shortenHomeInString(path)} (${content.length} chars)`

  return `${destinationPrefix} ${shortenHomeInString(path)}`
}

function resolveReadDetail(args: ToolArgs | undefined): string | undefined {
  const path = resolvePathArg(args)
  if (!path)
    return undefined

  return `from ${shortenHomeInString(path)}`
}

function resolveFirstDetail(args: ToolArgs | undefined, keys: string[]): string | undefined {
  for (const key of keys) {
    const value = coerceDisplayValue(lookupValueByPath(args, key))
    if (value)
      return shortenHomeInString(value)
  }

  return undefined
}

export function resolveToolDisplay(name: string, args?: unknown): ToolDisplay {
  const normalizedName = normalizeToolName(name)
  const toolKey = normalizedName.toLowerCase()
  const record = asRecord(args)
  const action = coerceDisplayValue(record?.action)

  let summary: string | undefined
  if (toolKey === 'bash') {
    summary = coerceDisplayValue(record?.command, 220)
  }
  else if (toolKey === 'read') {
    summary = resolveReadDetail(record)
  }
  else if (toolKey === 'write' || toolKey === 'edit' || toolKey === 'attach') {
    summary = resolveWriteDetail(toolKey, record)
  }
  else {
    summary = resolveFirstDetail(record, FALLBACK_DETAIL_KEYS)
  }

  const detailLines = [
    action ? `Action: ${action}` : undefined,
    record?.command ? `Command: ${coerceDisplayValue(record.command, 400)}` : undefined,
    summary ? `Detail: ${summary}` : undefined,
  ].filter((line): line is string => Boolean(line))

  return {
    title: defaultTitle(normalizedName),
    summary,
    detailLines,
  }
}
