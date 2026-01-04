<script setup lang="ts">
import { theme } from 'ant-design-vue'

import BootHeader from '@/components/Boot/Header.vue'
import LaunchCarousel from '@/components/Boot/LaunchCarousel.vue'

const { progress } = defineProps<{
  progress: number
}>()

const { token } = theme.useToken()
</script>

<template>
  <div class="flex flex-col w-full h-full bg-[#ECEDF4] dark:bg-[#141414]">
    <BootHeader />
    <div
      class="flex-1 bg-[#ffffff] dark:bg-[#1D1D1D] flex items-center justify-center"
    >
      <LaunchCarousel>
        <template #footer>
          <div class="mt-6 w-[280px]">
            <a-progress
              :percent="progress"
              :show-info="false"
              :stroke-color="token.colorPrimary"
            />
          </div>
        </template>
      </LaunchCarousel>
    </div>
  </div>
</template>
