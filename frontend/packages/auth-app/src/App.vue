<script setup lang="ts">
import { ConfigProvider } from '@rpa/components/config-provider'
import { Auth } from '@rpa/components/auth'
</script>

<template>
  <ConfigProvider>
    <Auth.LoginForm />
    <div class="flex items-center justify-center">xxxx</div>
  </ConfigProvider>
</template>
