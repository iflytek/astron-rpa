<script setup lang="ts">
import PageLayout from '../components/Base/PageLayout.vue'
import Login from '../components/Login/Index.vue'
import type { AuthType, Edition } from '../interface'

const { baseUrl, edition, authType } = defineProps({
  baseUrl: { type: String },
  edition: { type: String as () => Edition, default: 'saas' },
  authType: { type: String as () => AuthType, default: 'uap' },
})

const emit = defineEmits<{
  finish: []
}>()
</script>

<template>
  <PageLayout>
    <Login :base-url="baseUrl" :edition="edition" :auth-type="authType" @finish="() => emit('finish')" />
  </PageLayout>
</template>
