import { Button, theme } from 'ant-design-vue'
import { defineComponent } from 'vue'

export const IconButton = defineComponent({
  name: 'IconButton',
  props: {
    title: String,
    active: Boolean,
  },
  emits: ['click'],
  setup(props, { slots, emit }) {
    const { token } = theme.useToken()

    return () => (
      <Button
        type="text"
        size="small"
        title={props.title}
        class="inline-flex items-center justify-center"
        style={props.active ? { backgroundColor: token.value.colorFillSecondary, color: token.value.colorText } : null}
        onClick={() => emit('click')}
      >
        {slots.default?.()}
      </Button>
    )
  },
})
