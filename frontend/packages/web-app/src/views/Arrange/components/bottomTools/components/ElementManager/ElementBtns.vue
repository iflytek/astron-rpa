<script lang="ts" setup>
const props = defineProps<{ loading: boolean, disabled: boolean }>()
</script>

<template>
  <rpa-hint-icon name="add-circle" :loading="props.loading" :disabled="props.disabled" class="mr-1" enable-hover-bg>
    <template #suffix>
      <span class="ml-1">{{ $t("pickupNewElement") }}</span>
    </template>
  </rpa-hint-icon>
</template>
