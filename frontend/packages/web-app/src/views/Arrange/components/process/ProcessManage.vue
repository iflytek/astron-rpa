<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { ref } from 'vue'

import { ProcessModal } from '@/views/Arrange/components/process'

import ProcessTree from './processTree.vue'

const processModal = NiceModal.useModal(ProcessModal)

const menus = [
  {
    key: 'createChildProcess',
    icon: 'create-process',
    name: '新建流程',
    fn: () => processModal.show({ type: 'process' }),
  },
  {
    key: 'createPyCode',
    icon: 'create-python-process',
    name: '新建Python',
    fn: () => processModal.show({ type: 'module' }),
  },
]
const sidebarWide = ref(false)
</script>

<template>
  <section
    class="process-manage h-full bg-[#fff] dark:bg-[#1d1d1d]"
    :class="[sidebarWide ? 'w-[620px]' : 'w-80']"
  >
    <section class="process-manage-header flex items-center">
      <span
        class="process-title flex-1 text-[rgba(0, 0, 0, 0.85)] dark:text-[rgba(255,255,255,0.85)] mr-3 text-[16px] font-semibold h-[22px]"
      >流程管理</span>
      <rpa-hint-icon
        v-for="item in menus"
        :key="item.key"
        :name="item.icon"
        enable-hover-bg
        class="h-6 text-[12px] font-normal mr-2"
        @click="item.fn"
      >
        <template #suffix>
          <span class="new-process ml-1">{{ item.name }}</span>
        </template>
      </rpa-hint-icon>
      <rpa-hint-icon
        :name="sidebarWide ? 'sidebar-wide' : 'sidebar-narrow'"
        :title="sidebarWide ? '切换到窄版' : '切换到宽版'"
        enable-hover-bg
        width="16px"
        height="16px"
        @click="() => (sidebarWide = !sidebarWide)"
      />
    </section>
    <ProcessTree class="flex-1 flex flex-col overflow-hidden" />
  </section>
</template>

<style lang="scss" scoped>
.process-manage {
  display: flex;
  flex-direction: column;
  padding: 12px 16px;

  .process-manage-header {
    margin-bottom: 18px;

    .process-title {
      line-height: 22px;
    }

    .same-item {
      &:hover {
        color: $color-primary;
      }
    }
  }
}
</style>
