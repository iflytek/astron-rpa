import type { Level } from '@tiptap/extension-heading'
import type { Editor } from '@tiptap/vue-3'
import { Dropdown, Menu } from 'ant-design-vue'
import type { PropType } from 'vue'
import { computed, defineComponent } from 'vue'

import { IconButton } from '../../IconButton'

const HEADLINE_LEVEL: Level[] = [1, 2, 3]

const HEADLINE_LEVEL_TEXT: Record<Level, string> = {
  1: '一',
  2: '二',
  3: '三',
  4: '四',
  5: '五',
  6: '六',
}

export const HeadingToolbar = defineComponent({
  name: 'HeadingToolbar',
  props: {
    editor: {
      type: Object as PropType<Editor>,
      required: true,
    },
  },
  setup(props) {
    const { editor } = props

    const activeLevel = computed<Level | undefined>(() => {
      if (editor.isActive('paragraph')) {
        return undefined
      }

      for (let index = 0; index < HEADLINE_LEVEL.length; index++) {
        const level = HEADLINE_LEVEL[index]
        const isActive = editor.isActive('heading', { level })
        if (isActive) {
          return level
        }
      }

      return undefined
    })

    return () => (
      <Dropdown overlay={(
        <Menu class="w-24">
          <Menu.Item onClick={() => editor.chain().focus().setParagraph().run()}>正文</Menu.Item>
          <Menu.Divider />
          {HEADLINE_LEVEL.map(level => (
            <Menu.Item onClick={() => editor.chain().focus().toggleHeading({ level }).run()}>
              标题
              { HEADLINE_LEVEL_TEXT[level] }
            </Menu.Item>
          ))}
        </Menu>
      )}
      >
        <IconButton>{activeLevel.value ? `标题${HEADLINE_LEVEL_TEXT[activeLevel.value]}` : '正文' }</IconButton>
      </Dropdown>
    )
  },
})
