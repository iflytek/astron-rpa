<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { useToggle } from '@vueuse/core'

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

const [sidebarWide, toggleSidebarWide] = useToggle(false)
</script>

<template>
  <section
    class="process-manage h-full bg-[#fff] dark:bg-[#1d1d1d]"
    :class="[sidebarWide ? 'w-[620px]' : 'w-80']"
  >
    <section class="flex items-center mb-[18px]">
      <span class="flex-1 mr-3 text-[16px] font-semibold leading-[22px]">流程管理</span>
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
        @click="() => toggleSidebarWide()"
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
}
</style>
