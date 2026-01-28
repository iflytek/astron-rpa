<script setup lang="ts">
import { NiceModal } from "@rpa/components";
import type { FormInstance } from "ant-design-vue";
import { reactive, ref } from "vue";

interface FormState {
  name: string;
  password: string;
}

const modal = NiceModal.useModal();

const emit = defineEmits(["refresh"]);

const formRef = ref<FormInstance>();
const formState = reactive<FormState>({ name: "", password: "" });

async function handleOk() {
  await formRef.value?.validate();
  modal.hide();
  emit("refresh");
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="starAgentModal"
    :width="400"
    :mask-closable="false"
    :title="$t('settingCenter.voucherManage.createVoucher')"
    @ok="handleOk"
  >
    <a-form
      ref="formRef"
      :model="formState"
      autocomplete="off"
      layout="vertical"
      class="mt-[16px]"
    >
      <a-form-item :label="$t('voucherName')" name="name" required>
        <a-input
          v-model:value="formState.name"
          :placeholder="
            $t('common.enterPlaceholder', { name: $t('voucherName') })
          "
        />
      </a-form-item>
      <a-form-item :label="$t('password')" name="password" required>
        <a-input
          type="password"
          v-model:value="formState.password"
          :placeholder="$t('common.enterPlaceholder', { name: $t('password') })"
        />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
