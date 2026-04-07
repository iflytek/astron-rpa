<script setup lang="ts">
import { useTheme } from '@rpa/components'
import { onClickOutside } from '@vueuse/core'
import { computed, useTemplateRef } from 'vue'
import { storeToRefs } from 'pinia'

import PythonPackageManagement from '@/components/PythonPackageManagement/Index.vue'
import { useProcessStore } from '@/stores/useProcessStore'

import AtomForm from '../atomForm/AtomForm.vue'
import ProcessManage from '../process/ProcessManage.vue'
import CustomTabItem from '../rightTab/CustomTabItem.vue'
import CustomTabs from '../rightTab/CustomTabs.vue'
import VariableManage from '../variableManage/Index.vue'
import { RIGHT_TAB_KEY } from '../../config'

const processStore = useProcessStore()
const { rightTabActiveKey } = storeToRefs(processStore)

const { colorTheme } = useTheme()
const tabsRef = useTemplateRef('tabsRef')

const hasNodeParameter = computed(() => !!processStore.canvasManager.activeTab?.nodeParameter)

onClickOutside(tabsRef, (e) => {
  // 点击 "顶部工具栏/底部tab栏/流程切换栏/原子能力编辑页" 空白处关闭右侧tab
  const closeList = ['right-tab-close-area', 'ant-tabs-nav-wrap', 'virtual-scroll__wrapper']
  const target = e.target as HTMLElement
  const close = closeList.some(item => target.classList.contains(item)) && !!target.closest('.right-tab-close-area')
  if (close) {
    rightTabActiveKey.value = ''
  }
})
</script>

<template>
  <CustomTabs
    ref="tabsRef"
    v-model="rightTabActiveKey"
    position="right"
    class="custom-tabs dark:text-[rgba(255,255,255,0.65)]]"
    :class="[colorTheme]"
    double-click-clear
  >
    <CustomTabItem :show="hasNodeParameter" :name="$t('nodeParams')" :value="RIGHT_TAB_KEY.NODE" size="320">
      <AtomForm />
    </CustomTabItem>
    <CustomTabItem :name="$t('processManagement')" :value="RIGHT_TAB_KEY.PROCESS" size="320">
      <ProcessManage />
    </CustomTabItem>
    <CustomTabItem :name="$t('variableManagement')" :value="RIGHT_TAB_KEY.VARIABLE" size="620">
      <VariableManage />
    </CustomTabItem>
    <CustomTabItem :name="$t('pythonPackageManagement')" :value="RIGHT_TAB_KEY.PYTHON" size="620">
      <PythonPackageManagement />
    </CustomTabItem>
  </CustomTabs>
</template>

<style lang="scss" scoped>
.custom-tabs {
  --tab-padding-main: 0px;
  --tab-padding-cross: 10px;
  --text-color: rgba(0, 0, 0, 0.65);
  --active-text-color: rgba(0, 0, 0, 0.85);
  --divider-color: #ecedf4;
  --tab-bar-gap: 24px;

  width: 38px;
  overflow: visible;
  z-index: 1;

  :deep(.tabs-header) {
    padding-top: 20px;
    border-left: 2px solid #ecedf4;
    border-radius: 0 6px 6px 0;
    background-color: #ffffff;

    .tab-bar {
      width: 36px;
    }
  }

  :deep(.custom-tab-panel) {
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
    border-radius: 6px 0 0 6px;
    overflow: hidden;
  }
}

.dark.custom-tabs {
  --text-color: rgba(255, 255, 255, 0.65);
  --active-text-color: rgba(255, 255, 255, 0.85);
  --divider-color: #141414;

  :deep(.tabs-header) {
    background-color: rgba(#ffffff, 0.04);
    border-left: 2px solid #141414;
  }
}
</style>
