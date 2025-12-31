<script setup lang="ts">
import PageLayout from '../components/Base/PageLayout.vue'
import InviteForm from '../components/Invite/Index.vue'
import type { AuthType, Edition } from '../interface'

const { baseUrl, edition, authType } = defineProps({
  baseUrl: { type: String },
  edition: { type: String as () => Edition, default: 'saas' },
  authType: { type: String as () => AuthType, default: 'uap' },
})
</script>

<template>
  <PageLayout>
    <InviteForm :base-url="baseUrl" :edition="edition" :auth-type="authType" />
  </PageLayout>
</template>
