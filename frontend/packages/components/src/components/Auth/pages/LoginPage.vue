<script setup lang="ts">
import Login from '../components/Login/Index.vue'
import PageLayout from '../components/Base/PageLayout.vue'
import type { Edition, AuthType } from '../interface'

const props = defineProps({
  baseUrl: { type: String },
  edition: { type: String as () => Edition, default: 'saas' },
  authType: { type: String as () => AuthType, default: 'uap' },
})

</script>

<template>
  <PageLayout>
    <Login :base-url="baseUrl" :edition="edition" :auth-type="authType" />
  </PageLayout>
</template>
