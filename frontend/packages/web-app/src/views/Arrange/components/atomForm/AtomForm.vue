<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import type { Ref } from 'vue'
import { computed, inject, onMounted, ref, watch } from 'vue'

import BUS from '@/utils/eventBus'

import { useFlowStore } from '@/stores/useFlowStore'
import { renderBaseConfig, useBaseConfig } from '@/views/Arrange/components/atomForm/hooks/useBaseConfig'
import type { AtomTabs } from '@/views/Arrange/types/atomForm'

import AtomFormList from './AtomFormList.vue'

const { i18next, t } = useTranslation()
const isShowFormItem = inject<Ref<boolean>>('showAtomFormItem', ref(true))

const activeKey = ref<number>(0)
const sidebarWide = ref(false)
const flowStore = useFlowStore()
const atomTab = ref<AtomTabs[]>([])
const formattedTabs = computed(() => {
  return atomTab.value.map((item, index) => ({
    title: item.name,
    value: index,
  }))
})

watch(() => flowStore.activeAtom, (newVal) => {
  if (!newVal?.key) {
    BUS.$emit('toggleAtomForm', false)
  }
  renderForm(newVal)
  console.log(atomTab.value)
})

watch(() => flowStore.selectedAtomIds, () => {
  activeKey.value = 0
})

watch(() => isShowFormItem.value, () => {
  atomTab.value = renderBaseConfig(atomTab.value)
})

function renderForm(val) {
  atomTab.value = val ? useBaseConfig(val, t) : []
}

onMounted(() => {
  if (flowStore.activeAtom)
    renderForm(flowStore.activeAtom)
})
</script>

<template>
  <section class="atom-config h-full relative bg-[#fff] dark:bg-[#1d1d1d]" :class="sidebarWide ? 'w-[620px]' : 'w-80'">
    <section v-if="atomTab.length > 0" class="relative atom-config-container h-full overflow-y-auto py-3 px-4">
      <div class="flex items-center mb-4">
        <a-segmented v-model:value="activeKey" block :options="formattedTabs" class="flex-1">
          <template #label="{ title }">
            <span class="text-[12px]">{{ $t(title) }}</span>
          </template>
        </a-segmented>
        <rpa-hint-icon :name="sidebarWide ? 'sidebar-wide' : 'sidebar-narrow'" :title="sidebarWide ? '切换到窄版' : '切换到宽版'" class="ml-[12px]" width="16px" height="16px" enable-hover-bg @click="() => sidebarWide = !sidebarWide" />
      </div>
      <article
        v-for="item in atomTab[activeKey]?.params" :key="item.key"
        class="tab-container text-[#333] dark:text-[rgba(255,255,255,0.45)]"
      >
        <label v-if="item.name" class="tab-container-label dark:text-[rgba(255,255,255,0.85)] font-bold flex">
          {{ item.name[i18next.language] }}
        </label>
        <AtomFormList :atom-form="item.formItems" />
      </article>
    </section>
  </section>
</template>

<style lang="scss" scoped>
.atom-config {
  .atom-config-container {
    opacity: 1;

    .tab-container {
      font-size: 12px;
      margin-bottom: 24px;

      .tab-container-label {
        font-size: 14px;
        margin-bottom: 12px;
      }
    }

    &::-webkit-scrollbar {
      width: 4px;
    }

    // &::-webkit-scrollbar-thumb {
    //   background: #ccc;
    // }

    :deep(.ant-tabs-tab) {
      padding: 8px 16px;
    }

    :deep(.ant-tabs-tabpane) {
      padding: 0 10px 10px;
    }
  }

  .atom-config-rectangle {
    width: 20px;
    height: 50px;
    left: -20px;
    line-height: 50px;
    margin-top: -45px;
    font-size: 20px;
    color: #7d7d7d;
    background: #f2f2f2;
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
    z-index: 3;
  }
}
</style>
