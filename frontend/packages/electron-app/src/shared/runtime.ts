import type { ProviderId } from './settings'

export type CreateSessionInput = {
  title?: string | null
}

export type ComposerAttachment = {
  id: string
  name: string
  path: string
  mime: string
  url: string
}

export type SendMessageInput = {
  sessionID: string
  text: string
  attachments?: ComposerAttachment[]
  assistantId?: string | null
  roomId?: string | null
  agent?: string | null
  system?: string | null
  providerId?: ProviderId | null
  model?: string | null
}

export function buildPromptRequestBody(input: SendMessageInput) {
  const providerId = normalizeOptionalText(input.providerId)
  const model = normalizeOptionalText(input.model)
  const agent = normalizeOptionalText(input.agent)
  const system = normalizeOptionalText(input.system)
  const text = normalizeOptionalText(input.text)
  const fileParts = (input.attachments ?? []).map((attachment) => ({
    type: "file" as const,
    mime: attachment.mime,
    filename: attachment.name,
    url: attachment.url,
  }))
  const textParts = text ? [{ type: "text" as const, text }] : []
  const parts = [...fileParts, ...textParts]

  if (parts.length === 0) {
    throw new Error("Cannot send an empty message.")
  }

  return {
    ...(providerId && model ? { model: { providerID: providerId, modelID: model } } : {}),
    ...(agent ? { agent } : {}),
    ...(system ? { system } : {}),
    parts,
  }
}

function normalizeOptionalText(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : null
}
