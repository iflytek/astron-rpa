<script setup lang="ts">
import { Spin } from 'ant-design-vue'
import { computed, defineAsyncComponent } from 'vue'

import type { InfoInterface } from '../components/BasicInfo/index.vue'

import { useBasicStore } from './basicStore'

const BasicInfo = defineAsyncComponent(() => import('../components/BasicInfo/index.vue'))
const VersionRecord = defineAsyncComponent(() => import('../components/VersionRecord/Index.vue'))
const CreatorInfo = defineAsyncComponent(() => import('../components/CreatorInfo/Index.vue'))
const { loading, data } = useBasicStore()

const basicInfo = computed<InfoInterface>(() => ({
  robotName: data.value.name,
  versionNum: data.value.version,
  filePath: data.value.filePath,
  fileName: data.value.fileName,
  videoName: data.value.videoName,
  videoPath: data.value.videoPath,
  introduction: data.value.introduction,
  useDescription: data.value.useDescription,
}))
</script>

<template>
  <section v-if="!loading" class="flex flex-col gap-4">
    <BasicInfo :data="basicInfo" />
    <VersionRecord v-bind="data" :version-info-list="data.versionList" />
    <CreatorInfo v-bind="data" />
  </section>
  <section v-else class="h-96 flex items-center justify-center">
    <Spin />
  </section>
</template>
