<script setup lang="ts">
import { Button } from 'ant-design-vue'
import { inject } from 'vue'

const loginStep = inject('loginStepFn', (...args) => args)

function registerFn() {
  loginStep('register')
}
</script>

<template>
  <Button type="link" class="Login-right_register" @click="registerFn">
    {{ $t("signUp") }}
  </Button>
</template>
