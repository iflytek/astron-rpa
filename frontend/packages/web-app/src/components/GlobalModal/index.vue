<!--
 目前项目中针对弹窗主要有三种形式：
1. 在需要使用 <a-modal></a-modal> 的地方不用改还是按照之前的用法，无感知替换；
2. 在需要使用 <Modal></Modal> 的地方，引入 GlobalModal/index.vue，替换成<Global></Global>；
3. 在需要使用 类似Modal.confirm({...}) 的地方，引入 GlobalModal/index.ts，替换成GlobalModal.confirm({...})；
这三种形式都默认配置centered:true,keyborad:false；如果后续出现需要修改的情况，可自行配置这两个属性覆盖默认配置
-->
<script lang="ts" setup>
import type { ModalProps } from 'ant-design-vue'
import { Modal } from 'ant-design-vue'

// 改为运行时 props 声明，这样在 TSX 中类型推断更稳定
const props = defineProps({
  // 继承 Modal 的所有 props
  ...({} as ModalProps),
  // 允许任意额外属性
} as {
  [K in keyof ModalProps]?: ModalProps[K]
} & {
  [key: string]: any
})
</script>

<template>
  <Modal
    class="global-modal"
    :keyboard="false"
    :centered="true"
    v-bind="props"
  >
    <template v-for="slotName in Object.keys($slots)" :key="slotName" #[slotName]="slotData">
      <slot
        :name="slotName"
        v-bind="slotData && typeof slotData === 'object' ? slotData : {}"
      />
    </template>
  </Modal>
</template>

<style lang="scss">
/* 统一header和footer的外边距，content的边距自己开发的时候按照UI自己设置 */
.global-modal {
  .ant-modal-header {
    margin: 0 0 16px 0;
  }
  .ant-modal-footer {
    margin: 16px 0 0 0;
  }
}
</style>
