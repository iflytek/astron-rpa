import { provide, ref } from 'vue'

function useArrangeProvide() {
  provide('showAtomFormItem', ref(true)) // 显示原子能力项
  provide('showAtomConfig', ref(false)) // 右侧原子能力配置表单
}

export default useArrangeProvide
