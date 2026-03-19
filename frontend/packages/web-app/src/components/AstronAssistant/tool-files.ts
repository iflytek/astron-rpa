export type ToolFilePreviewKind = 'text' | 'pdf'

export interface ToolFileArtifact {
  title: string
  path: string
  content: string | null
  createdAt: number
  previewKind: ToolFilePreviewKind
}

type ToolArgs = Record<string, unknown>
const PREVIEWABLE_TOOL_NAMES = new Set([
  'write',
  'edit',
  'attach',
  'read',
  'exec',
  'bash',
  'process',
])
const PATH_MATCHERS = [
  /[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]+\.(?:pdf|txt|md|markdown|json|yaml|yml|log|ini|cfg|conf|csv|xml|html|js|ts|py|sh|ps1)\b/gi,
  /(?:\/[^/\s"'`]+)+\/[^/\s"'`]+\.(?:pdf|txt|md|markdown|json|yaml|yml|log|ini|cfg|conf|csv|xml|html|js|ts|py|sh|ps1)\b/gi,
] as const

function asRecord(value: unknown): ToolArgs | undefined {
  return value && typeof value === 'object' ? value as ToolArgs : undefined
}

function coerceString(value: unknown): string | undefined {
  if (typeof value !== 'string')
    return undefined

  const trimmed = value.trim()
  return trimmed || undefined
}

function resolvePathArg(args: ToolArgs | undefined): string | undefined {
  if (!args)
    return undefined

  for (const candidate of [args.path, args.file_path, args.filePath, args.to, args.url]) {
    const value = coerceString(candidate)
    if (value)
      return value
  }

  return undefined
}

function collectCandidateStrings(value: unknown, results: string[], depth = 0) {
  if (depth > 4 || value == null)
    return

  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (trimmed)
      results.push(trimmed)
    return
  }

  if (Array.isArray(value)) {
    for (const item of value)
      collectCandidateStrings(item, results, depth + 1)
    return
  }

  if (typeof value === 'object') {
    for (const nested of Object.values(value as ToolArgs))
      collectCandidateStrings(nested, results, depth + 1)
  }
}

function extractPreviewablePathFromText(input: string): string | undefined {
  for (const matcher of PATH_MATCHERS) {
    const matches = input.match(matcher)
    if (!matches)
      continue

    for (const match of matches) {
      const normalized = match.trim().replace(/^['"`]+|['"`]+$/g, '')
      if (resolvePreviewKind(normalized))
        return normalized
    }
  }

  return undefined
}

function resolvePathFromArgsOrOutput(
  args: ToolArgs | undefined,
  output: string,
): string | undefined {
  const directPath = resolvePathArg(args)
  if (directPath && isPreviewableFile(directPath))
    return directPath

  const candidates: string[] = []
  collectCandidateStrings(args, candidates)
  if (output.trim())
    candidates.push(output)

  for (const candidate of candidates) {
    const extractedPath = extractPreviewablePathFromText(candidate)
    if (extractedPath)
      return extractedPath
  }

  return undefined
}

function resolveTextContent(args: ToolArgs | undefined, output: string): string | null {
  if (!args) {
    return output.trim() || null
  }

  for (const candidate of [args.content, args.newText, args.new_string, args.text]) {
    const value = coerceString(candidate)
    if (value)
      return value
  }

  return output.trim() || null
}

function fileNameFromPath(path: string): string {
  const normalized = path.replace(/[\\/]+$/, '')
  const parts = normalized.split(/[\\/]/)
  return parts.at(-1) || path
}

function resolvePreviewKind(path: string): ToolFilePreviewKind | null {
  const lower = path.toLowerCase()
  if (lower.endsWith('.pdf'))
    return 'pdf'

  if ([
    '.txt',
    '.md',
    '.markdown',
    '.json',
    '.yaml',
    '.yml',
    '.log',
    '.ini',
    '.cfg',
    '.conf',
    '.csv',
    '.xml',
    '.html',
    '.js',
    '.ts',
    '.py',
    '.sh',
    '.ps1',
  ].some(ext => lower.endsWith(ext))) {
    return 'text'
  }

  return null
}

function isPreviewableFile(path: string): boolean {
  return resolvePreviewKind(path) !== null
}

export function resolveToolFileArtifact(params: {
  toolName: string
  args?: unknown
  output?: string
  createdAt: number
}): ToolFileArtifact | null {
  const toolKey = params.toolName.trim().toLowerCase()
  if (!PREVIEWABLE_TOOL_NAMES.has(toolKey))
    return null

  const args = asRecord(params.args)
  const path = resolvePathFromArgsOrOutput(args, params.output ?? '')
  if (!path || !isPreviewableFile(path))
    return null

  const previewKind = resolvePreviewKind(path)
  if (!previewKind)
    return null

  return {
    title: fileNameFromPath(path),
    path,
    content:
      previewKind === 'text'
        ? resolveTextContent(args, params.output ?? '')
        : null,
    createdAt: params.createdAt,
    previewKind,
  }
}
