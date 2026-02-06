<script setup lang="ts">
import PageLayout from '../components/Base/PageLayout/Index.vue'
import InviteForm from '../components/Invite/Index.vue'
import type { AuthType, Edition, Platform } from '../interface'

const { baseUrl, edition, authType, platform } = defineProps({
  platform: { type: String as () => Platform },
  baseUrl: { type: String },
  edition: { type: String as () => Edition, default: 'saas' },
  authType: { type: String as () => AuthType, default: 'uap' },
})
</script>

<template>
  <PageLayout>
    <InviteForm :base-url="baseUrl" :platform="platform" :edition="edition" :auth-type="authType" />
  </PageLayout>
</template>
