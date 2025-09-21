<script lang="ts" setup>
import UserForm from '@/views/Arrange/components/customDialog/components/userFormDialog.vue'
import ConfigProvider from '@/components/ConfigProvider/index.vue'
</script>

<template>
  <ConfigProvider>
    <UserForm />
  </ConfigProvider>
</template>

<style lang="scss">
#user-form {
  width: 100%;
  height: 100%;
}
</style>
