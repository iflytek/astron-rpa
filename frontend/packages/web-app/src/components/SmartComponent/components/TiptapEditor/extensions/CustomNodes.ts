import { Node } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'

import DescriptionDom from '../DescriptionNode.vue'
import ElementDom from '../ElementNode.vue'

// 目标区域节点
export const ElementNode = Node.create({
  name: 'elementNode',
  inline: true,
  group: 'inline',
  content: 'inline*',
  defining: true,

  addAttributes() {
    return {
      name: {
        default: '目标区域',
      },
      imageUrl: {
        default: '',
      },
      xpath: {
        default: '',
      },
      outerHtml: {
        default: '',
      },
      elementId: {
        default: '',
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="element"]',
        getAttrs: dom => ({
          name: dom.getAttribute('data-name'),
          imageUrl: dom.getAttribute('data-image-url') || '',
          xpath: dom.getAttribute('data-xpath') || '',
          outerHtml: dom.getAttribute('data-outer-html') || '',
          elementId: dom.getAttribute('data-element-id') || '',
        }),
      },
    ]
  },

  renderHTML({ node }) {
    return ['div', {
      'data-type': 'element',
      'data-name': node.attrs.name,
      'data-image-url': node.attrs.imageUrl,
      'data-xpath': node.attrs.xpath,
      'data-outer-html': node.attrs.outerHtml,
      'data-element-id': node.attrs.elementId,
    }, 0]
  },

  addCommands() {
    return {
      insertElementNode: (attrs: any = {}) => ({ chain }: any) => {
        return chain()
          .insertContent({
            type: this.name,
            attrs: {
              name: attrs.name || '元素名',
              imageUrl: attrs.imageUrl || '',
              xpath: attrs.xpath || '',
              outerHtml: attrs.outerHtml || '',
              elementId: attrs.elementId || '',
            },
          })
          .run()
      },
    } as any
  },

  addNodeView() {
    return VueNodeViewRenderer(ElementDom)
  },
})

// 文本描述节点
export const DescriptionNode = Node.create({
  name: 'descriptionNode',
  inline: true,
  group: 'inline',
  content: 'inline*',

  parseHTML() {
    return [
      {
        tag: 'div[data-type="description"]',
      },
    ]
  },

  renderHTML() {
    return ['div', {
      'data-type': 'description',
    }, 0]
  },

  addCommands() {
    return {
      insertDescriptionNode: (attrs: any = {}) => ({ chain }: any) => {
        const content = attrs.content || '可见元素的自动化操作'
        return chain()
          .insertContent({
            type: this.name,
            content: [
              {
                type: 'text',
                text: content,
              },
            ],
          })
          .run()
      },
    } as any
  },

  addNodeView() {
    return VueNodeViewRenderer(DescriptionDom)
  },
})
