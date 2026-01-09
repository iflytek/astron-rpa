<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import type { Ref } from 'vue'
import { computed, inject, ref, watch } from 'vue'

import BUS from '@/utils/eventBus'

import AtomFormList from '@/views/Arrange/components/atomForm/AtomFormList.vue'
import { renderBaseConfig, useBaseConfig } from '@/views/Arrange/components/atomForm/hooks/useBaseConfig'
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

function renderForm(atom: RPA.Atom) {
  atomTab.value = atom ? useBaseConfig(atom, t) : []
}

watch(() => isShowFormItem.value, () => {
  atomTab.value = renderBaseConfig(atomTab.value)
})

watch(() => props.atom, (newVal, oldVal) => {
  if (!newVal?.key) {
    BUS.$emit('toggleAtomForm', false)
  }
  if (newVal?.key !== oldVal?.key) {
    activeKey.value = 0
  }
  renderForm(newVal)
  console.log('atomForm', atomTab.value)
}, { immediate: true })

const alias = computed(() => atomTab.value
  .find(item => item.key === 'baseParam')
  .params[0]
  .formItems
  .find(item => item.key === 'anotherName')
  .value[0]
  .value,
)

watch(() => alias.value, (newVal, oldVal) => {
  if (newVal !== oldVal) {
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
