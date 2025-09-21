<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { storeToRefs } from 'pinia'
import type { Ref } from 'vue'
import { computed, inject, onMounted, ref, watch } from 'vue'

import { getComponentPreviewForm } from '@/utils/customComponent'

import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import AtomFormList from '@/views/Arrange/components/atomForm/AtomFormList.vue'
import { renderBaseConfig, useBaseConfig } from '@/views/Arrange/components/atomForm/hooks/useBaseConfig'
import type { AtomTabs } from '@/views/Arrange/types/atomForm'

const emit = defineEmits<{
  (evt: 'toggleWidth', e: boolean)
}>()

const { i18next, t } = useTranslation()
const isShowFormItem = inject<Ref<boolean>>('showAtomFormItem', ref(true))
const { parameters } = storeToRefs(useProcessStore())

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
// const extraFormItem = {
//   types: 'Browser',
//   formType: {
//     type: 'RESULT',
//   },
//   key: 'edit_desc',
//   title: '编辑区便捷描述',
//   tip: '',
//   value: [
//     {
//       type: 'var',
//       value: '',
//     },
//   ],
// }

watch(() => parameters.value, () => {
  renderForm(mockAtom.value)
}, { deep: true })

watch(() => flowStore.selectedAtomIds, () => {
  activeKey.value = 0
})

watch(() => isShowFormItem.value, () => {
  atomTab.value = renderBaseConfig(atomTab.value)
})

function renderForm(val) {
  atomTab.value = val ? useBaseConfig(val, t) : []
}

const mockAtom = computed(() => {
  return getComponentPreviewForm({
    componentId: useProcessStore().project.id,
    componentName: useProcessStore().project.name,
    componentAttrs: parameters.value,
  })
})

function toggleWidth() {
  sidebarWide.value = !sidebarWide.value
  emit('toggleWidth', sidebarWide.value)
}

onMounted(() => {
  renderForm(mockAtom.value)
})
</script>

<template>
  <section class="atom-config flex-1 flex flex-col w-full relative bg-[#fff] dark:bg-[#1d1d1d] overflow-hidden">
    <section v-if="atomTab.length > 0" class="flex-1 relative atom-config-container border border-dashed border-[#000000]/[.16] dark:border-[#FFFFFF]/[.16] rounded-[8px] h-full overflow-y-auto py-5 px-4">
      <div class="flex items-center mb-4">
        <a-segmented v-model:value="activeKey" block :options="formattedTabs" class="flex-1">
          <template #label="{ title }">
            <span class="text-[12px]">{{ $t(title) }}</span>
          </template>
        </a-segmented>
        <rpa-hint-icon :name="sidebarWide ? 'sidebar-wide' : 'sidebar-narrow'" :title="sidebarWide ? '切换到窄版' : '切换到宽版'" class="ml-[12px]" width="16px" height="16px" enable-hover-bg @click="toggleWidth" />
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
    <!-- <section class="mt-4">
      <AtomFormItem v-if="activeKey === 0" :atom-form-item="extraFormItem" />
    </section> -->
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
