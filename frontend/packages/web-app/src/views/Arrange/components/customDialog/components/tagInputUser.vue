<script lang="tsx">
import { reactive } from 'vue'
import type { VNode } from 'vue'

export default {
  name: 'TagInputUser',
  props: {
    itemData: {
      type: Object,
      default() {
        return {}
      },
    },
    suffix: {
      type: Object as () => VNode,
    },
  },
  setup(props) {
    const { itemData } = reactive({
      ...props,
    })
    const { defaultValue, placeholder } = itemData
    const defaultVal = defaultValue
    const getCotent = () => {
      if (!defaultVal.length) {
        return (
          <div style="color: #d9d9d9; font-size: 12px; padding: 0 4px;">{placeholder}</div>
        )
      }
      return (
        <div>
          {
            defaultVal.map((item) => {
              return item.type === 'var' ? <hr class="dialog-tag-input-hr" data-name={item.value}></hr> : item.value
            })
          }
        </div>
      )
    }
    const IntroFn = () => {
      return (
        <div
          class="tag-input bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)]"
          contenteditable={true}
        >
          { getCotent() }
          {
            props.suffix && <div>{props.suffix}</div>
          }
        </div>
      )
    }
    return () => IntroFn()
  },
}
</script>

<style lang="scss" scoped>
.tag-input {
  outline: none;
  padding: 4px 8px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 32px;

  &:hover {
    border-color: #1890ff;
  }
}
</style>
