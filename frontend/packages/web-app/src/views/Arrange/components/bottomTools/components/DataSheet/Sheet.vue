<script lang="ts" setup>
import { Sheet, useTheme } from '@rpa/components'

const props = defineProps<{ height: number }>()

const { isDark } = useTheme()
</script>

<template>
  <Sheet :style="{ height: `${props.height}px` }" :dark-mode="isDark" />
</template>