<template>
  <a-select
    v-model:value="modelValue"
    :mode="props.renderData.formType.params?.multiple ? 'multiple' : undefined"
    placeholder="请选择"
    class="bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)] rounded-[8px]"
    style="width: 100%"
  >
    <a-select-option
      v-for="(op, index) in options"
      :key="index"
      :value="op?.label ? op.value : op.rId"
    >
      <template v-if="op?.label">
        {{ op.label }}
      </template>
      <template v-else>
        <span v-for="(it, idx) in op.value.value" :key="idx">
          <hr
            v-if="it.type === 'var'"
            class="dialog-tag-input-hr"
            :data-name="it.value"
          />
          <span v-else>{{ it.value }}</span>
        </span>
      </template>
    </a-select-option>
  </a-select>
</template>

<script setup lang="ts">
import { SelectValue } from "ant-design-vue/es/select";
import { shallowRef, onBeforeMount } from "vue";
import { get } from "lodash-es";

import { getCredentialList } from "@/api/engine";

const modelValue = defineModel<SelectValue>("value");
const props = defineProps<{ renderData: RPA.AtomDisplayItem }>();

const options = shallowRef(props.renderData.options);

const paramFilers = get(props.renderData, "formType.params.filters", []);

onBeforeMount(async () => {
  if (paramFilers.includes("credential")) {
    const data = await getCredentialList();
    options.value = data.map((item) => ({
      label: item.name,
      value: item.name,
    }));
  }
});
</script>
