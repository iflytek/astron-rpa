<script lang="ts" setup>
defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <rpa-hint-icon name="add-circle" :loading="loading" :disabled="disabled" class="mr-1" enable-hover-bg>
    <template #suffix>
      <span class="ml-1">{{ $t("pickupNewElement") }}</span>
    </template>
  </rpa-hint-icon>
</template>
