interface MessageContentBlock {
  type?: string
  text?: string
}

export function extractTextFromOpenClawMessage(message: any): string {
  if (!message || typeof message !== 'object')
    return ''

  if (typeof message.text === 'string' && message.text.trim())
    return message.text.trim()

  if (typeof message.content === 'string' && message.content.trim())
    return message.content.trim()

  const content = Array.isArray(message.content)
    ? (message.content as MessageContentBlock[])
    : []
  return content
    .map((item) => {
      if (!item || typeof item !== 'object')
        return null
      if (item.type === 'text' && typeof item.text === 'string')
        return item.text
      return null
    })
    .filter((item): item is string => Boolean(item?.trim()))
    .join('\n')
    .trim()
}
