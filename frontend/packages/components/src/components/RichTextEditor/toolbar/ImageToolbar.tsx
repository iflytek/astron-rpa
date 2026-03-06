import { PictureOutlined } from '@ant-design/icons-vue'
import type { Editor } from '@tiptap/vue-3'
import { Upload } from 'ant-design-vue'
import i18next from 'i18next'
import type { PropType } from 'vue'
import { defineComponent } from 'vue'

import { IconButton } from '../../IconButton'

export const ImageToolbar = defineComponent({
  name: 'ImageToolbar',
  props: {
    editor: {
      type: Object as PropType<Editor>,
      required: true,
    },
    uploadFile: {
      type: Function as PropType<(file: File) => Promise<string>>,
      required: true,
    },
  },
  setup(props) {
    const addImage = (url: string) => {
      props.editor.chain().focus().setImage({ src: url }).run()
    }

    const beforeUpload = (file: File) => {
      props.uploadFile(file).then(url => addImage(url))
      return false
    }

    return () => (
      <Upload showUploadList={false} maxCount={1} multiple={false} beforeUpload={beforeUpload} accept="image/*">
        <IconButton title={i18next.t('components.richText.insertImage')}>
          <PictureOutlined />
        </IconButton>
      </Upload>
    )
  },
})
