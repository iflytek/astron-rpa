<script setup lang="ts">
import { computed } from "vue";
import { isEmpty } from 'lodash-es'

import { useFormStore } from "./hooks/useFormStore";

const props = defineProps<{
  atomFormMeta: RPA.Process.AtomTabs;
}>()

const { nodeParameter } = useFormStore();

// 查找是否存在模版
const template = computed(() => {
  const formItems = props.atomFormMeta.params.map(item => item.formItems).flat();
  const templateItem = formItems.find(item => !isEmpty(item.formType?.params?.templates))
  if (!templateItem) {
    return null
  }
  return {
    key: templateItem.key,
    templates: templateItem.formType?.params?.templates || [],
  }
})

const handleTemplateClick = (key: string, template: RPA.AtomFormAITemplate) => {
  nodeParameter.value?.updateValue(key, template.value)
}
</script>

<template>
  <div v-if="template">
    <label class="leading-6 text-text-secondary">试一试</label>
    <div class="mt-2 space-x-3">
      <a-button
        class="px-2"
        v-for="item in template.templates"
        :key="item.key"
        @click="handleTemplateClick(template.key, item)"
      >
        {{ item.label }}
      </a-button>
    </div>
  </div>
</template>
