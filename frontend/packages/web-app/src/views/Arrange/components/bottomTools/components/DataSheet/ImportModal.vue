<script lang="ts" setup>
import { NiceModal, type ISheetWorkbookData } from "@rpa/components";
import { reactive, ref } from "vue";

const props = defineProps<{ workbookData: ISheetWorkbookData }>();
const emits = defineEmits<{
  (e: "import", payload: { sheetId: string; firstRowAsHeader: boolean }): void;
}>();

const formRef = ref();

const modal = NiceModal.useModal();

const sheetOptions = Object.values(props.workbookData.sheets).map((sheet) => ({
  label: sheet.name,
  value: sheet.id,
}));

const formState = reactive({
  selectedSheet: sheetOptions[0]?.value || null,
  firstRowAsHeader: false,
});

const handleOk = async () => {
  await formRef.value.validate();
  emits("import", {
    sheetId: formState.selectedSheet,
    firstRowAsHeader: formState.firstRowAsHeader,
  });
  modal.hide();
};
</script>

<template>
  <a-modal v-bind="NiceModal.antdModal(modal)" title="数据导入" @ok="handleOk">
    <a-form ref="formRef" layout="vertical" :model="formState">
      <a-form-item label="请选择需要导入的 sheet" required>
        <a-select v-model:value="formState.selectedSheet" :options="sheetOptions" />
      </a-form-item>
      <a-checkbox v-model:checked="formState.firstRowAsHeader">设置第一行为列名</a-checkbox>
    </a-form>
  </a-modal>
</template>
