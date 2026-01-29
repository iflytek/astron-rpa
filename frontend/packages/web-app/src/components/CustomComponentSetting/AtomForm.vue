<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import type { Ref } from 'vue'
import { computed, inject, ref, watch } from 'vue'

import BUS from '@/utils/eventBus'

import AtomFormItem from '@/views/Arrange/components/atomForm/AtomFormItem.vue'
import { renderBaseConfig, useBaseConfig } from '@/views/Arrange/components/atomForm/hooks/useBaseConfig'
import type { AtomTabs } from '@/views/Arrange/types/atomForm'

const props = defineProps<{
  atom: RPA.Atom
  showCollapse?: boolean
}>()

const emit = defineEmits<{
  (e: 'collapse', v: boolean)
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
    <div class="flex items-center gap-2">
      <a-segmented v-model:value="activeKey" block :options="formattedTabs" class="flex-1">
        <template #label="{ title }">
          <span class="text-[12px]">{{ $t(title) }}</span>
        </template>
      </a-segmented>
      <rpa-hint-icon
        v-if="showCollapse"
        :title="$t('common.collapse')"
        name="navigate-expand"
        enable-hover-bg
        class="p-1.5"
        @click="emit('collapse', true)" />
    </div>

    <div class="form-container flex-1 flex flex-col gap-6 overflow-y-auto">
      <section
        v-for="item in atomTab[activeKey]?.params"
        :key="item.key"
        class="text-[12px]"
      >
        <label v-if="item.name" class="text-[14px] font-bold mb-3 inline-block">
          {{ item.name[i18next.language] }}
        </label>
        <template
          v-for="form in item.formItems?.filter(item => !item.dynamics || [undefined, true].includes(item.show))"
          :key="form.key"
        >
          <template v-if="item.key.startsWith('input') || item.key.startsWith('output')">
            <div class="group relative p-1.5" @click="">
              <AtomFormItem :atom-form-item="form" disabled />
              <div class="absolute inset-0 rounded-lg hover:bg-[#5D59FF]/[.35] cursor-pointer"></div>
              <rpa-icon
                name="edit-outline"
                size="20"
                class="invisible group-hover:visible absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none"
              />
            </div>
          </template>
          <template v-else>
            <AtomFormItem :atom-form-item="form" disabled />
          </template>
        </template>
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
  