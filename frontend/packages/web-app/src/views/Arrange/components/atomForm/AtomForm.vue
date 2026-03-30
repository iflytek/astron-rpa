<script setup lang="ts">
import { NiceModal } from "@rpa/components";
import { storeToRefs } from "pinia";

import { useProcessStore } from "@/stores/useProcessStore";

import AtomBaseForm from "./AtomBaseForm.vue";
import AtomFooter from "./AtomFooter.vue";
import { AtomFormModal } from "./modals";

const processStore = useProcessStore();

const { rightTabActiveKey } = storeToRefs(processStore);

const handleToggleCollapsed = () => {
  NiceModal.show(AtomFormModal);
};

const handleClose = () => {
  rightTabActiveKey.value = "";
};
</script>

<template>
  <AtomBaseForm
    class="atom-config h-full relative bg-white dark:bg-[#1d1d1d] w-[400px]"
    headerClass="pt-4 px-4"
    bodyClass="px-4 pb-4"
    :collapsed="true"
    @toggleCollapsed="handleToggleCollapsed"
    @close="handleClose"
  >
    <template #footer>
      <AtomFooter class="px-6 py-3" />
    </template>
  </AtomBaseForm>
</template>
