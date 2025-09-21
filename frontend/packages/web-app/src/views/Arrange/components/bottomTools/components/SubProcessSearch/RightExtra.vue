<script lang="ts" setup>
import { useProcessStore } from '@/stores/useProcessStore.ts'
</script>

<template>
  <rpa-hint-icon name="close" enable-hover-bg @click="useProcessStore().closeSearchSubProcess" />
</template>
