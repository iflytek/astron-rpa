import { defineComponent, onMounted, ref, watch } from 'vue'
import '@rpa/components/icon'

export const Icon = defineComponent({
  name: 'RIcon',
  props: {
    // 图标名称
    name: { type: String, required: true },
    // 表示所渲染的 svg 图形宽高，默认1em，有效值的格式参考svg元素的宽度/高度取值。如果图标比例非1:1，建议略过此值，直接设置width，height
    size: { type: String },
    // 表示所渲染的svg图形宽度，默认1em，优先级高于size
    width: { type: String },
    // 表示所渲染的svg图形高度，默认1em，优先级高于size
    height: { type: String },
    // 表示是否为 svg 添加旋转动画（旋转动画为无限循环），默认为false。
    spin: { type: Boolean, default: false },
    // 表示所渲染的svg图形中需要变色区域的颜色。有效值的格式参考svg元素的stroke/fill 取值。
    color: { type: String },
    // 表示所渲染的 svg 图形中需要变色区域的 stroke 颜色，优先级高于 color 。
    stroke: { type: String },
    // 表示所渲染的 svg 图形中需要变色区域的 fill 颜色，优先级高于 color 。
    fill: { type: String },
    // 默认图标，当指定图标不存在时使用
    defaultName: { type: String, default: 'atom-default' },
  },
  emits: ['click'],
  setup(props, { emit }) {
    const currentIconName = ref(props.name)

    function checkIcon() {
      if (!props.name)
        return
      if (!document.getElementById(props.name)) {
        currentIconName.value = props.defaultName
      }
      else {
        currentIconName.value = props.name
      }
    }

    watch(() => props.name, () => {
      currentIconName.value = props.name
      checkIcon()
    })

    onMounted(() => {
      // 延迟检查，确保 SVG sprite 已加载
      setTimeout(() => {
        checkIcon()
      }, 100)
    })

    return () => (
      <svg
        name={props.name}
        class={['r-icon inline-block', { 'animate-spin': props.spin }]}
        style={props.color ? { color: props.color } : {}}
        width={props.width || props.size || '1em'}
        height={props.height || props.size || '1em'}
        fill={props.fill}
        stroke={props.stroke}
        onClick={() => emit('click')}
      >
        <use href={`#${currentIconName.value}`}></use>
      </svg>
    )
  },
})
