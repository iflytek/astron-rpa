<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { onClickOutside } from '@vueuse/core'
import { Drawer } from 'ant-design-vue'
import { computed, ref, useTemplateRef } from 'vue'

import AtomForm from './AtomForm.vue'
import AtomFormItem from '@/views/Arrange/components/atomForm/AtomFormItem.vue'
import { useProcessStore } from '@/stores/useProcessStore'
import { getComponentPreviewForm } from '@/utils/customComponent'
import { exampleFormList as exampleFormListRaw } from './exampleFormList'

const exampleFormList = ref(exampleFormListRaw.map(item => ({ ...item })))

const props = defineProps<{ clickOutsideIgnoreSelector?: string }>()

const modal = NiceModal.useModal()
const container = useTemplateRef('container')

const mockAtom = computed(() => {
  const { project, parameters } = useProcessStore()
  return getComponentPreviewForm({
    componentId: project.id,
    componentName: project.name,
    componentAttrs: parameters,
  })
})

const descriptionForm = ref({
  formType: { type: 'INPUT_VARIABLE' },
  key: 'comment',
  name: 'comment',
  required: false,
  tip: '编辑区便捷描述',
  title: '编辑区便捷描述',
  types: 'Str',
  value: [],
})


onClickOutside(
  container,
  (event) => {
    const target = event.target as HTMLElement
    
    // Ant Design Vue 浮层组件类名列表
    const floatingComponentSelectors = [
      '.ant-popover',           // Popover 气泡卡片
      '.ant-select-dropdown',   // Select 选择器
      '.ant-dropdown',          // Dropdown 下拉菜单
      '.ant-picker-dropdown',   // DatePicker/TimePicker 日期/时间选择框
      '.ant-cascader-dropdown', // Cascader 级联选择
      '.ant-tooltip',           // Tooltip 文字提示
      '.ant-modal-wrap',        // Modal 对话框
    ]
    
    // 检查点击的元素是否在浮层组件内
    const isInFloatingComponent = floatingComponentSelectors.some(selector =>
      target.closest(selector),
    )
    
    // 检查是否在自定义忽略选择器内
    const isInCustomIgnore = props.clickOutsideIgnoreSelector
      ? target.closest(props.clickOutsideIgnoreSelector)
      : false
    
    // 如果点击在浮层组件或自定义忽略区域内，不关闭弹窗
    if (isInFloatingComponent || isInCustomIgnore) {
      return
    }
    
    modal.hide()
  },
)
</script>

<template>
  <Drawer
    v-bind="NiceModal.antdDrawer(modal)"
    :width="355"
    :mask="false"
    :header-style="{ display: 'none' }"
    :content-wrapper-style="{
      margin: 0,
      top: '88px',
      boxShadow: '-3px 0 6px -4px rgba(0, 0, 0, 0.12)',
    }"
    :style="{ borderRadius: '6px' }"
    :body-style="{ padding: 0 }"
  >
    <div ref="container" class="h-full flex flex-col overflow-hidden">
      <div class="m-4 mb-0 text-sm leading-6">
        {{ $t("components.customComponentSetting") }}
      </div>
      <div
        class="flex-1 m-3 py-5 px-4 border border-dashed border-[#000000]/[.16] dark:border-[#FFFFFF]/[.16] rounded overflow-hidden"
      >
        <AtomForm :atom="mockAtom" show-collapse @collapse="modal.hide()" />
      </div>
      <section class="mx-4 mb-5">
        <AtomFormItem
          :atom-form-item="descriptionForm"
          class="text-[12px]"
        />
      </section>

      <!-- <section class="mx-4 mb-5 overflow-y-auto max-h-[400px]">
        <div
          v-for="item in exampleFormList"
          :key="item.key"
          class="mb-4 p-3 border border-[#000000]/[.08] dark:border-[#FFFFFF]/[.08] rounded-lg bg-[#fafafa] dark:bg-[#1a1a1a]"
        >
          <AtomFormItem
            :atom-form-item="item"
            class="text-[12px]"
          />
          <div class="mt-2 pt-2 border-t border-[#000000]/[.08] dark:border-[#FFFFFF]/[.08]">
            <div class="text-[10px] text-[#000000]/[.45] dark:text-[#FFFFFF]/[.45] mb-1">
              Value (实时):
            </div>
            <pre class="text-[10px] text-[#000000]/[.85] dark:text-[#FFFFFF]/[.85] bg-[#ffffff] dark:bg-[#2a2a2a] p-2 rounded overflow-x-auto max-h-[120px] overflow-y-auto font-mono whitespace-pre-wrap break-words">{{ item.value }}</pre>
            <div class="text-[9px] text-[#000000]/[.35] dark:text-[#FFFFFF]/[.35] mt-1">
              类型: {{ Array.isArray(item.value) ? 'Array' : typeof item.value }}
            </div>
          </div>
        </div>
      </section> -->
    </div>
  </Drawer>
</template>
