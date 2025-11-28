<script setup lang="ts">
import { computed } from 'vue'

import AtomFormItem from './AtomFormItem.vue'

const { atomForm } = defineProps<{ atomForm: RPA.AtomDisplayItem[] }>()

const atomFormItem = computed(() => atomForm.filter(item => item.show !== false))
</script>

<template>
  <AtomFormItem v-for="item in atomFormItem" :key="item.key" :atom-form-item="item" />
</template>
