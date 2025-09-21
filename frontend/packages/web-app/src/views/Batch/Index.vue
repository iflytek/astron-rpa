<script lang="ts" setup>
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import DataBatch from '@/components/DataBatch/Index.vue'
</script>

<template>
  <ConfigProvider>
    <div class="p-batch h-screen">
      <div class="h-full bg-bg-elevated rounded-md shadow-md flex flex-col  overflow-hidden box-border">
        <DataBatch />
      </div>
    </div>
  </ConfigProvider>
</template>

<style lang="scss">
#app-batch {
  width: 100%;
  height: 100%;
  background-color: transparent;
}
.p-batch {
  padding: 4px 8px 8px 4px;
}
</style>
