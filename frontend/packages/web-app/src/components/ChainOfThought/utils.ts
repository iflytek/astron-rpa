export interface SearchResult {
  title: string
  url: string
}

export interface StepData {
  searchResults?: SearchResult[]
  imageBase64?: string
  imageMediaType?: string
  imageCaption?: string
  content?: string
}

export interface Step {
  id: string
  type: 'search' | 'image' | 'text' | 'thinking'
  label: string
  status: 'pending' | 'active' | 'complete'
  data?: StepData
}

export interface PartialToolCall {
  name: string
  args: string
  stepId: string | null
}

const logoDevToken = 'live_6a1a28fd-6420-4492-aeb0-b297461d9de2'

export function getLogoSrc(website: string): string {
  try {
    const hostname = getHostname(website)
    if (!logoDevToken)
      return `https://img.logo.dev/${hostname}`
    return `https://img.logo.dev/${hostname}?token=${logoDevToken}`
  }
  catch {
    return ''
  }
}

export function getHostname(website: string): string {
  try {
    return new URL(website).hostname
  }
  catch {
    return website
  }
}

let stepCounter = 0

export function createStep(type: Step['type'], label: string, data?: StepData): Step {
  return {
    id: `step-${++stepCounter}`,
    type,
    label,
    status: 'active',
    data,
  }
}

export function formatToolCallLabel(name: string, args: string): string {
  try {
    const parsed = JSON.parse(args)
    if (parsed.query)
      return `搜索: ${parsed.query}`
    if (parsed.url)
      return `访问: ${parsed.url}`
    if (parsed.command)
      return `执行: ${parsed.command}`
    if (parsed.action)
      return `操作: ${parsed.action}`
  }
  catch {
    // args are not yet valid JSON
  }
  return `调用工具: ${name}`
}

export function parseSearchResults(args: string): SearchResult[] {
  try {
    const parsed = JSON.parse(args)
    if (Array.isArray(parsed.results)) {
      return parsed.results.map((r: any) => ({
        title: r.title ?? r.url ?? '',
        url: r.url ?? '',
      }))
    }
    if (parsed.query) {
      return [{ title: parsed.query, url: `https://www.google.com/search?q=${encodeURIComponent(parsed.query)}` }]
    }
  }
  catch {
    // ignore
  }
  return []
}

export interface StreamContext {
  steps: Step[]
  partialToolCalls: Record<number, PartialToolCall>
  currentTextStepId: string | null
}

export async function processStreamResponse(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  context: StreamContext
) {
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done)
      break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const rawLine of lines) {
      const line = rawLine.trim()
      if (!line.startsWith('data:'))
        continue

      const data = line.slice(5).trim()
      if (processSseMessage(data, context))
        return
    }
  }
}

export function processSseMessage(
  data: string,
  context: StreamContext
): boolean {
  if (data === '[DONE]') {
    return true
  }

  let json: any
  try {
    json = JSON.parse(data)
  }
  catch {
    return false
  }

  const delta = json.choices?.[0]?.delta
  if (!delta)
    return false

  // reasoning_content (thinking)
  if (delta.reasoning_content) {
    if (context.currentTextStepId) {
      const existing = context.steps.find(s => s.id === context.currentTextStepId)
      if (existing && existing.type === 'thinking') {
        existing.data = existing.data ?? {}
        existing.data.content = (existing.data.content ?? '') + delta.reasoning_content
      }
      else {
        if (existing)
          existing.status = 'complete'
        const thinkingStep = createStep('thinking', '思考中…', { content: delta.reasoning_content })
        context.steps.push(thinkingStep)
        context.currentTextStepId = thinkingStep.id
      }
    }
    else {
      const thinkingStep = createStep('thinking', '思考中…', { content: delta.reasoning_content })
      context.steps.push(thinkingStep)
      context.currentTextStepId = thinkingStep.id
    }
  }

  // content (text)
  if (delta.content) {
    if (context.currentTextStepId) {
      const existing = context.steps.find(s => s.id === context.currentTextStepId)
      if (existing && existing.type === 'text') {
        existing.data = existing.data ?? {}
        existing.data.content = (existing.data.content ?? '') + delta.content
      }
      else {
        if (existing)
          existing.status = 'complete'
        const textStep = createStep('text', delta.content, { content: delta.content })
        context.steps.push(textStep)
        context.currentTextStepId = textStep.id
      }
    }
    else {
      const textStep = createStep('text', delta.content, { content: delta.content })
      context.steps.push(textStep)
      context.currentTextStepId = textStep.id
    }
  }

  // tool_calls
  if (delta.tool_calls) {
    if (context.currentTextStepId) {
      const existing = context.steps.find(s => s.id === context.currentTextStepId)
      if (existing)
        existing.status = 'complete'
      context.currentTextStepId = null
    }

    for (const tc of delta.tool_calls) {
      const idx: number = tc.index ?? 0
      if (!context.partialToolCalls[idx]) {
        const name = tc.function?.name ?? 'tool_call'
        const label = formatToolCallLabel(name, '')
        const searchStep = createStep('search', label)
        context.steps.push(searchStep)
        context.partialToolCalls[idx] = {
          name,
          args: tc.function?.arguments ?? '',
          stepId: searchStep.id,
        }
      }
      else {
        context.partialToolCalls[idx].args += tc.function?.arguments ?? ''
        const partial = context.partialToolCalls[idx]
        const step = context.steps.find(s => s.id === partial.stepId)
        if (step) {
          step.label = formatToolCallLabel(partial.name, partial.args)
        }
      }
    }
  }

  // finish_reason
  const finishReason = json.choices?.[0]?.finish_reason
  if (finishReason && finishReason !== 'null') {
    for (const partial of Object.values(context.partialToolCalls)) {
      const step = context.steps.find(s => s.id === partial.stepId)
      if (step) {
        step.status = 'complete'
        step.label = formatToolCallLabel(partial.name, partial.args)
        const results = parseSearchResults(partial.args)
        if (results.length > 0)
          step.data = { searchResults: results }
      }
    }
    return true
  }

  return false
}
