<script setup lang="ts">
import { ref, computed, h, useTemplateRef, nextTick } from "vue";
import { useToggle } from "@vueuse/core";

import AtomNotice from "./AtomNotice.vue";
import AtomFormRender from "./AtomFormRender.vue";
import AtomTestRender from "./AtomTestRender.vue";
import { useProvideFormStore } from "./hooks/useFormStore";

const props = defineProps<{ collapsed?: boolean, headerClass?: string, bodyClass?: string }>();

const emit = defineEmits(["close", "toggleCollapsed"]);

const { atom, atomTab, nodeParameter } = useProvideFormStore();

const activeKey = ref<string | number>(0);
const inputRef = useTemplateRef<HTMLInputElement>('inputRef')
const [isEdit, toggleEdit] = useToggle(false);

const formattedTabs = computed(() => {
  const formTabs = atomTab.value.map((item, index) => ({
    title: item.name,
    value: index,
    render: () => h(AtomFormRender, { atomFormMeta: item })
  }))
  const testTab = {
    title: '调试结果',
    value: 'test',
    render: () => h(AtomTestRender)
  }

  return atom.value.debugButton ? [...formTabs, testTab] : formTabs
})

const atomName = computed(() => atom.value?.alias || atom.value?.title);
const activeTab = computed(() => formattedTabs.value.find(item => item.value === activeKey.value))

const handleAliasChange = (e: FocusEvent) => {
  const alias = (e.target as HTMLInputElement).value?.trim()
  if (alias && alias !== atomName.value) {
    nodeParameter.value.updateAlias(alias)
  }
  toggleEdit(false)
}

const handleAliasEdit = () => {
  toggleEdit(true)
  nextTick(() => inputRef.value?.focus())
}
</script>

<template>
  <div class="relative atom-config-container flex flex-col">
    <div :class="props.headerClass">
      <div class="h-8 mb-2 flex gap-2 items-center">
        <div
          class="w-6 h-6 mr-1 rounded-lg bg-primary inline-flex items-center justify-center"
        >
          <rpa-icon :name="atom.icon" class="text-white text-base" />
        </div>

        <a-input
          v-if="isEdit"
          ref="inputRef"
          :default-value="atomName"
          class="max-w-[300px] w-auto"
          size="small"
          @press-enter="toggleEdit(false)"
          @blur="handleAliasChange"
        />
        <div v-else class="truncate text-base font-semibold">
          {{ atomName }}
        </div>
        <a-tooltip :title="atom.title" v-if="atom.alias">
          <rpa-icon name="info" class="text-base text-text-tertiary" />
        </a-tooltip>
        <rpa-icon
          name="edit-outlined"
          class="text-base cursor-pointer text-text-secondary"
          @click="!isEdit && handleAliasEdit()"
        />

        <rpa-hint-icon
          :name="props.collapsed ? 'maximize' : 'minimize'"
          :title="props.collapsed ? '切换到宽版' : '切换到窄版'"
          class="text-base mx-1 ml-auto"
          enable-hover-bg
          @click="() => emit('toggleCollapsed')"
        />
        <rpa-hint-icon
          name="close-1"
          class="text-base mx-1"
          enable-hover-bg
          @click="() => emit('close')"
        />
      </div>

      <div class="text-text-secondary mb-3 truncate">{{ atom.comment }}</div>

      <AtomNotice class="mb-6" />

      <a-segmented
        v-model:value="activeKey"
        block
        :options="formattedTabs"
        class="mb-6"
      >
        <template #label="{ title }">
          <span class="text-[12px]">{{ $t(title) }}</span>
        </template>
      </a-segmented>
    </div>

    <div class="flex-1 min-h-0 overflow-y-auto" :class="props.bodyClass">
      <component :is="activeTab?.render()" />
    </div>

    <slot name="footer" />
  </div>
</template>

<style lang="scss" scoped>
.atom-config-container {
  opacity: 1;

  .tab-container {
    font-size: 12px;
    margin-bottom: 24px;
  }

  &::-webkit-scrollbar {
    width: 4px;
  }

  :deep(.ant-tabs-tab) {
    padding: 8px 16px;
  }

  :deep(.ant-tabs-tabpane) {
    padding: 0 10px 10px;
  }
}
</style>
