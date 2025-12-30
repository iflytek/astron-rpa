<script setup lang="ts">
import { Auth } from '@rpa/components/auth'

const ENV = import.meta.env
</script>

<template>
  <Auth.InvitePage :auth-type="ENV.VITE_AUTH_TYPE" :edition="ENV.VITE_EDITION" />
</template>
