<script lang="ts" setup>
import { onMounted } from 'vue'

import { windowManager } from '@/platform'

import { useCloseApp } from '../HeaderControl/useCloseApp'

const { closeApp } = useCloseApp()

function windowCloseWatch() {
  windowManager.onWindowClose(() => closeApp())
}

onMounted(() => windowCloseWatch())
</script>

<template>
  <div style="display: none" />
</template>
