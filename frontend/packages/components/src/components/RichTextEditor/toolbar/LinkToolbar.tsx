import { LinkOutlined } from '@ant-design/icons-vue'
import type { Editor } from '@tiptap/vue-3'
import { Button, Form, Input, Popover } from 'ant-design-vue'
import i18next from 'i18next'
import type { PropType } from 'vue'
import { defineComponent, reactive, ref } from 'vue'

import { IconButton } from '../../IconButton'

interface FormState {
  text: string
  url: string
}

export const LinkToolbar = defineComponent({
  name: 'LinkToolbar',
  props: {
    editor: {
      type: Object as PropType<Editor>,
      required: true,
    },
  },
  setup(props) {
    const { editor } = props
    const open = ref(false)
    const formState = reactive<Partial<FormState>>({})

    const onFinish = () => {
      const { text, url } = formState
      if (text && url) {
        editor.chain().focus().deleteSelection().insertContent(text).run()
        const position = editor.state.selection.$anchor.pos - text.length
        editor.chain().focus().setTextSelection({ from: position, to: position + text.length }).setLink({ href: url }).run()

        open.value = false
      }
    }

    const renderContent = () => (
      <Form layout="vertical" model={formState} onFinish={onFinish} class="w-80">
        <Form.Item label={i18next.t('components.richText.text')}>
          <Input v-model={[formState.text, 'value']} placeholder={i18next.t('components.richText.addDesc')} />
        </Form.Item>
        <Form.Item label={i18next.t('components.richText.link')}>
          <Input v-model={[formState.url, 'value']} placeholder={i18next.t('components.richText.linkUrl')} />
        </Form.Item>
        <Form.Item class="m-0">
          <Button htmlType="submit" disabled={!formState.text || !formState.url}>{i18next.t('components.richText.confirm')}</Button>
        </Form.Item>
      </Form>
    )

    const handleOpenChange = (_open: boolean) => {
      open.value = _open

      if (_open) {
        const selection = editor.state.selection
        const { from, to } = selection
        formState.text = editor.state.doc.textBetween(from, to, ' ')
        formState.url = editor.getAttributes('link').href
      }
    }

    return () => (
      <Popover
        open={open.value}
        arrow={false}
        content={renderContent()}
        placement="bottomLeft"
        trigger="click"
        onOpenChange={handleOpenChange}
      >
        <IconButton title={i18next.t('components.richText.insertLink')}>
          <LinkOutlined />
        </IconButton>
      </Popover>
    )
  },
})
