<script setup lang="ts">
import { Spin } from 'ant-design-vue'
import { defineAsyncComponent } from 'vue'

import { useBasicStore } from './basicStore'

const BasicInfo = defineAsyncComponent(() => import('../components/BasicInfo/index.vue'))
const VersionRecord = defineAsyncComponent(() => import('../components/VersionRecord/Index.vue'))
const CreatorInfo = defineAsyncComponent(() => import('../components/CreatorInfo/Index.vue'))
const { loading, data } = useBasicStore()
</script>

<template>
  <section v-if="!loading" class="flex flex-col gap-4">
    <BasicInfo :data="data" />
    <VersionRecord v-bind="data" />
    <CreatorInfo v-bind="data" />
  </section>
  <section v-else class="h-96 flex items-center justify-center">
    <Spin />
  </section>
</template>
