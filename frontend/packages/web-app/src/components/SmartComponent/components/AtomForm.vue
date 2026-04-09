<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { isEmpty } from 'lodash-es'
import type { Ref } from 'vue'
import { computed, inject, ref, watch } from 'vue'

import BUS from '@/utils/eventBus'

import AtomFormList from '@/views/Arrange/components/atomForm/AtomFormList.vue'
import type { AtomTabs } from '@/views/Arrange/types/atomForm'

const props = defineProps<{
  atom: RPA.Atom
}>()

const { i18next, t } = useTranslation()
const isShowFormItem = inject<Ref<boolean>>('showAtomFormItem', ref(true))

const activeKey = ref<number>(0)
const atomTab = ref<AtomTabs[]>([])
const formattedTabs = computed(() => atomTab.value.map((item, index) => ({
  title: item.name,
  value: index,
})))

/**
 * 根据原子能力数据生成表单 tabs 配置
 */
function generateFormTabs(atom: RPA.Atom): AtomTabs[] {
  if (!atom) return []

  const { inputList = [], outputList = [], advanced = [], exception = [], noAdvanced } = atom

  const baseParam: AtomTabs = {
    key: 'baseParam',
    name: 'basicParameters',
    params: [
      {
        name: { 'zh-CN': '输入信息', 'en-US': 'Input information' },
        key: `input-${atom.key}`,
        id: atom.id ?? '',
        atomKey: atom.key ?? '',
        formItems: inputList,
      },
      {
        name: { 'zh-CN': '输出信息', 'en-US': 'Output information' },
        key: `output-${atom.key}`,
        formItems: outputList,
      },
    ],
  }

  const advancedParam: AtomTabs = {
    key: 'advancedParam',
    name: 'advancedParameters',
    params: [
      {
        key: `advanced-${atom.key}`,
        formItems: advanced,
      },
    ],
  }

  const exceptionParam: AtomTabs = {
    key: 'exceptParam',
    name: 'exceptionHandling',
    params: [
      {
        key: `exception-${atom.key}`,
        formItems: exception,
      },
    ],
  }

  let tabs: AtomTabs[] = noAdvanced ? [baseParam] : [baseParam, advancedParam, exceptionParam]

  // 过滤空的 formItems
  tabs = tabs.map(item => ({
    ...item,
    params: item.params.filter(param => !isEmpty(param.formItems)),
  }))

  // 过滤空的 params
  tabs = tabs.filter(item => !isEmpty(item.params))

  return tabs
}

function renderForm(atom: RPA.Atom) {
  atomTab.value = atom ? generateFormTabs(atom) : []
}

watch(() => props.atom, (newVal, oldVal) => {
  if (!newVal?.key) {
    BUS.$emit('toggleAtomForm', false)
  }
  if (newVal?.key !== oldVal?.key) {
    activeKey.value = 0
  }
  renderForm(newVal)
}, { immediate: true })

const alias = computed(() => {
  const baseParam = atomTab.value.find(item => item.key === 'baseParam')
  const baseInfo = baseParam?.params.find(p => p.formItems?.some(f => f.key === 'anotherName'))
  const anotherNameItem = baseInfo?.formItems?.find(item => item.key === 'anotherName')
  return anotherNameItem?.value?.[0]?.value
})

watch(() => alias.value, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    props.atom.alias = newVal
  }
}, { deep: true })
</script>

<template>
  <div v-if="atomTab.length > 0" class="h-full flex flex-col gap-4 bg-bg-elevated">
    <a-segmented v-model:value="activeKey" block :options="formattedTabs">
      <template #label="{ title }">
        <span class="text-[12px]">{{ $t(title) }}</span>
      </template>
    </a-segmented>

    <div class="form-container flex-1 flex flex-col gap-6 overflow-y-auto">
      <section
        v-for="item in atomTab[activeKey]?.params"
        :key="item.key"
        class="text-[12px]"
      >
        <label v-if="item.name" class="text-[14px] font-bold mb-3 inline-block">
          {{ item.name[i18next.language] }}
        </label>
        <AtomFormList :atom-form="item.formItems" />
      </section>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.form-container {
  padding-right: 2px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  :deep(.form-container-label-name) {
    color: var(--text-text-tertiary);
  }
}
</style>
