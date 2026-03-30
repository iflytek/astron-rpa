<script setup lang="ts">
import { useTranslation } from "i18next-vue";

import AtomFormItem from "./AtomFormItem.vue";
import AtomTemplate from "./AtomTemplate.vue";
import { useFormStore } from "./hooks/useFormStore";

const { i18next } = useTranslation();
const { nodeParameter } = useFormStore();

const props = defineProps<{ atomFormMeta: RPA.Process.AtomTabs }>()
</script>

<template>
  <div class="space-y-6">
    <AtomTemplate :atomFormMeta="props.atomFormMeta" />
    <div
      v-for="item in props.atomFormMeta.params"
      :key="item.key"
      class="tab-container text-[#333] dark:text-[rgba(255,255,255,0.45)]"
    >
      <div
        v-if="item.name"
        class="text-sm leading-6 mb-3 flex gap-1 items-center"
      >
        <span class="w-1 h-3 rounded-[1px] bg-primary" />
        {{ item.name[i18next.language] }}
      </div>
      <template v-for="it in item.formItems" :key="it.key">
        <AtomFormItem
          v-if="it.show !== false"
          :atom-form-item="it"
          @update="nodeParameter?.updateValue"
        />
      </template>
    </div>
  </div>
</template>
