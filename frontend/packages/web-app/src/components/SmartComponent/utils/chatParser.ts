import type {
  DocNode,
  ElementAttrs,
  Message,
  MessageInput,
  MessageOutput,
  ParsedQuestion,
} from '../types'

/**
 * 解析TiptapEditor的JSON格式为服务端需要的格式
 */
export function parseChatContent(editorJson: DocNode): ParsedQuestion {
  const elements: Array<ElementAttrs> = []
  const elementSet = new Set<string>()

  let userText = ''

  // 遍历文档内容
  if (editorJson.content && Array.isArray(editorJson.content)) {
    editorJson.content.forEach((paragraph) => {
      if (paragraph.type === 'paragraph' && paragraph.content) {
        paragraph.content.forEach((node) => {
          if (node.type === 'text') {
            // 普通文本节点
            userText += node.text
          }
          else if (node.type === 'elementNode') {
            // 元素节点
            const elementNode = node
            const attrs = node.attrs

            const uniqueKey = attrs.elementId || attrs.xpath

            if (!elementSet.has(uniqueKey)) {
              elementSet.add(uniqueKey)
              elements.push(attrs)
            }

            // 在用户文本中用反引号包围元素名称
            userText += `\`${elementNode.attrs.name}\``
          }
          else if (node.type === 'descriptionNode') {
            // 描述节点
            const descriptionNode = node
            // 从节点内容中提取文本
            if (descriptionNode.content && Array.isArray(descriptionNode.content)) {
              descriptionNode.content.forEach((textNode: any) => {
                if (textNode.type === 'text') {
                  userText += textNode.text
                }
              })
            }
          }
          else if (node.type === 'filePathNode') {
            const filePathNode = node
            userText += filePathNode.attrs.path
          }
        })
      }
    })
  }

  return {
    user: userText.trim(),
    elements,
  }
}

/**
 * 将 MessageInput 的 user 文本转换为 DocNode
 * user 文本格式：普通文本 + `元素名`（由 parseChatContent 生成）
 */
export function parseUserTextToDocNode(userText: string, elements: ElementAttrs[]): DocNode {
  // 从传入的 elements 数组构建元素映射表
  const elementMap = new Map<string, ElementAttrs>()
  elements.forEach((element) => {
    elementMap.set(element.name, element)
  })

  // 按行分割文本
  const lines = userText.split('\n')
  const paragraphs: any[] = []

  lines.forEach((line) => {
    const isBlankLine = !line.trim()

    if (isBlankLine) {
      // 空行：如果上一个段落有内容，创建一个空段落；否则跳过
      if (paragraphs.length > 0 && paragraphs[paragraphs.length - 1].content.length > 0) {
        paragraphs.push({
          type: 'paragraph',
          content: [],
        })
      }
      return
    }

    const nodes: any[] = []
    let currentIndex = 0

    // 匹配 `元素名` 格式（由 parseChatContent 生成的格式）
    const pattern = /`([^`]+)`/g
    let match = pattern.exec(line)

    while (match !== null) {
      // 添加匹配前的文本
      if (match.index > currentIndex) {
        const textBefore = line.substring(currentIndex, match.index)
        if (textBefore) {
          nodes.push({
            type: 'text',
            text: textBefore,
          })
        }
      }

      // 处理匹配到的元素名
      const elementName = match[1]
      const elementAttrs = elementMap.get(elementName)

      if (elementAttrs) {
        // 如果找到了元素，创建 elementNode
        nodes.push({
          type: 'elementNode',
          attrs: elementAttrs,
        })
      }
      else {
        // 如果找不到元素，保持原样作为文本（包含反引号）
        nodes.push({
          type: 'text',
          text: match[0],
        })
      }

      currentIndex = match.index + match[0].length
      match = pattern.exec(line)
    }

    // 添加剩余的文本
    if (currentIndex < line.length) {
      const textAfter = line.substring(currentIndex)
      if (textAfter) {
        nodes.push({
          type: 'text',
          text: textAfter,
        })
      }
    }

    // 如果当前行没有任何节点
    if (nodes.length === 0) {
      nodes.push({
        type: 'text',
        text: line,
      })
    }

    // 创建新段落
    paragraphs.push({
      type: 'paragraph',
      content: nodes,
    })
  })

  // 如果没有段落，创建一个空段落
  if (paragraphs.length === 0) {
    paragraphs.push({
      type: 'paragraph',
      content: [],
    })
  }

  return {
    type: 'doc',
    content: paragraphs,
  }
}

/**
 * 解析服务端返回的优化提问结果，转换为TiptapEditor的JSON格式
 */
export function parseOptimizedTextToDocNode(text: string, elements: ElementAttrs[]): DocNode {
  // 提取代码块中的内容
  const codeBlockMatch = text.match(/```new_prompt\s*([\s\S]*?)```/)
  const contentText = codeBlockMatch ? codeBlockMatch[1].trim() : text.trim()

  // 从传入的 elements 数组构建元素映射表
  const elementMap = new Map<string, ElementAttrs>()
  elements.forEach((element) => {
    elementMap.set(element.name, element)
  })

  // 按行分割文本
  const lines = contentText.split('\n')
  const paragraphs: any[] = []

  lines.forEach((line) => {
    const isBlankLine = !line.trim()

    if (isBlankLine) {
      // 空行：如果上一个段落有内容，创建一个空段落；否则跳过
      if (paragraphs.length > 0 && paragraphs[paragraphs.length - 1].content.length > 0) {
        paragraphs.push({
          type: 'paragraph',
          content: [],
        })
      }
      return
    }

    const nodes: any[] = []
    let currentIndex = 0

    // 匹配 `{元素名:elementId}` 或 `{元素名}` 和 `[文本内容]` 的模式
    const pattern = /`(\{([^}:]+)(?::([^}]+))?\}|\[([^\]]+)\])`/g
    let match = pattern.exec(line)

    while (match !== null) {
      // 添加匹配前的文本
      if (match.index > currentIndex) {
        const textBefore = line.substring(currentIndex, match.index)
        if (textBefore) {
          nodes.push({
            type: 'text',
            text: textBefore,
          })
        }
      }

      // 处理匹配到的内容
      if (match[1].startsWith('{')) {
        // `{元素名:elementId}` 或 `{元素名}` -> elementNode
        const elementName = match[2]
        const elementIdFromText = match[3]

        let elementAttrs = elementMap.get(elementName)

        if (!elementAttrs) {
          elementAttrs = {
            name: elementName,
            imageUrl: '',
            xpath: '',
            outerHtml: '',
            elementId: elementIdFromText || '',
          }
        }

        nodes.push({
          type: 'elementNode',
          attrs: elementAttrs,
        })
      }
      else if (match[1].startsWith('[')) {
        // `[文本内容]` -> descriptionNode
        const descriptionContent = match[4]
        nodes.push({
          type: 'descriptionNode',
          content: [
            {
              type: 'text',
              text: descriptionContent,
            },
          ],
        })
      }

      currentIndex = match.index + match[0].length
      match = pattern.exec(line)
    }

    // 添加剩余的文本
    if (currentIndex < line.length) {
      const textAfter = line.substring(currentIndex)
      if (textAfter) {
        nodes.push({
          type: 'text',
          text: textAfter,
        })
      }
    }

    // 如果当前行没有任何节点
    if (nodes.length === 0) {
      nodes.push({
        type: 'text',
        text: line,
      })
    }

    // 创建新段落
    paragraphs.push({
      type: 'paragraph',
      content: nodes,
    })
  })

  // 如果没有段落，创建一个空段落
  if (paragraphs.length === 0) {
    paragraphs.push({
      type: 'paragraph',
      content: [],
    })
  }

  return {
    type: 'doc',
    content: paragraphs,
  }
}

export function isAssistantMessage(item: Message): item is { role: 'assistant', content: MessageOutput } {
  return item?.role === 'assistant'
}

export function isUserMessage(item: Message): item is { role: 'user', content: MessageInput } {
  return item?.role === 'user'
}
