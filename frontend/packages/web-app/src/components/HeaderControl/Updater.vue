<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import { UpdaterModal } from '@/components/Updater'

const handleClick = () => {
  NiceModal.show(UpdaterModal, {
    needUpdate: true,
    latestVersion: 'v1.1.3'
  })
}
</script>

<template>
  <a-tooltip title="点击查看新版本">
    <div class="w-[22px] h-[22px] rounded-3xl bg-primary flex items-center justify-center cursor-pointer" @click="handleClick">
      <rpa-icon name="arrow-up" class="w-[14px] h-[14px] text-white" />
    </div>
  </a-tooltip>
</template>
