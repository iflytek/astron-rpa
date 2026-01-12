<script lang="ts" setup>
import ConfigProvider from '@/components/ConfigProvider/index.vue'

import UserFormWindow from './UserFormWindow.vue'
</script>

<template>
  <ConfigProvider>
    <UserFormWindow />
  </ConfigProvider>
</template>

<style lang="scss">
#user-form {
  width: 100%;
  height: 100%;
}
</style>
