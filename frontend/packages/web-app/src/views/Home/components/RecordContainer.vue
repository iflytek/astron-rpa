<script setup lang="ts">
import Banner from './Banner.vue'
import TableContainer from './TableContainer.vue'
</script>

<template>
  <div class="h-full flex flex-col z-10 relative">
    <Banner
      :title="$t('designerManage.regularExecution')"
      :sub-title="$t('designerManage.simpleAsSettingAlarm')"
    />
    <TableContainer>
      <slot />
    </TableContainer>
  </div>
</template>
