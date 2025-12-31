// TiptapEditor 相关的类型定义

export interface ElementAttrs {
  name: string
  imageUrl: string
  xpath: string
  outerHtml: string
  elementId: string
}

export interface ElementNode {
  type: 'elementNode'
  attrs: ElementAttrs
}

export interface DescriptionNode {
  type: 'descriptionNode'
  content?: Array<{ type: 'text', text: string }>
}

export interface TextNode {
  type: 'text'
  text: string
}

export interface FilePathNode {
  type: 'filePathNode'
  attrs: {
    type: 'file' | 'folder'
    path: string
  }
}

export interface ParagraphNode {
  type: 'paragraph'
  content: (TextNode | ElementNode | DescriptionNode | FilePathNode)[]
}

export interface DocNode {
  type: 'doc'
  content: ParagraphNode[]
}

export interface ParsedQuestion {
  user: string
  elements: Array<ElementAttrs>
}
