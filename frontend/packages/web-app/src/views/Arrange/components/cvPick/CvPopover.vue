<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { computed, onMounted, ref } from 'vue'
import { useToggle } from '@vueuse/core'

import { ELEMENT_IN_TYPE } from '@/constants/atom'
import { useCvStore } from '@/stores/useCvStore'
import type { Element } from '@/types/resource'

import CvPickBtn from './CvPickBtn.vue'
import CvTree from './CvTree.vue'
import CvUploadBtn from './CvUploadBtn.vue'

interface CvPopoverProps {
  renderData: RPA.AtomDisplayItem
  renderType?: string
  showAddBtn?: boolean
  itemChosed?: string
}

export interface SelectedElement {
  type: string
  value: string
  data: string
}

const props = withDefaults(defineProps<CvPopoverProps>(), {
  renderType: '',
  showAddBtn: true,
  itemChosed: '',
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select', selected: SelectedElement[]): void
}>()

const cvStore = useCvStore()
const { t } = useTranslation()

const searchValue = ref<string>('')
const [collapsed, toggleCollapsed] = useToggle(true)

function handleSelect({ name, id }: Element) {
  emit('select', [{ type: ELEMENT_IN_TYPE, value: name, data: id }])
  closePopover()
}

const cvTreeData = computed(() => {
  if (!searchValue.value) return cvStore.cvTreeData
  
  return cvStore
    .cvTreeData
    .map((i) => ({
      ...i,
      elements: i.elements.filter(i =>
        i.name.toLowerCase().includes(searchValue.value.toLowerCase()),
      ),
    }))
    .filter(i => i.elements.length > 0)
})

function closePopover() {
  emit('close')
}

onMounted(() => cvStore.getCvTreeData())
</script>

<template>
  <div class="w-[230px]">
    <div class="flex items-center">
      <a-input
        v-model:value="searchValue"
        class="text-xs"
        :placeholder="t('searchElements')"
      />
      <rpa-hint-icon
        name="expand-bottom"
        :title="collapsed ? '全部收起' : '全部展开'"
        class="ml-[12px]"
        :class="[collapsed ? 'rotate-180' : 'rotate-0']"
        enable-hover-bg
        @click="toggleCollapsed()"
      />
      <CvPickBtn v-if="props.showAddBtn" type="icon" enable-hover-bg />
      <CvUploadBtn v-if="props.showAddBtn" type="icon" enable-hover-bg />
    </div>
    <CvTree
      class="mt-2.5 h-[230px]"
      item-action-type="delete"
      :tree-data="cvTreeData"
      :item-chosed="props.itemChosed"
      :collapsed="!searchValue && collapsed"
      :disabled-contextmenu="true"
      :element-actions="['edit', 'delete']"
      @click="handleSelect"
      @action-click="closePopover"
    />
  </div>
</template>
