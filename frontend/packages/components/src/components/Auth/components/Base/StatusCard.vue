<script setup lang="ts">
import { Button } from 'ant-design-vue'

import { Icon as RpaIcon } from '../../../Icon'

interface Props {
  status: string
  title: string
  desc?: string
  buttonTxt?: string
}

const { title, desc, buttonTxt, status } = defineProps<Props>()

const emit = defineEmits<{
  click: []
}>()
</script>

<template>
  <div
    class="status-card text-center rounded-[16px]
    w-full h-auto
    md:bg-[#ffffff] dark:md:bg-[#000000] md:shadow-lg md:w-[400px] md:h-full md:p-[40px] "
  >
    <div class="my-[40px]" :class="!buttonTxt ? 'md:mt-[80px]' : ''">
      <div class="w-full h-[160px] relative">
        <RpaIcon
          class="inline-block w-[305px] h-[235px] absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2"
          :class="{
            '!w-[355px] !h-[245px]': ['joined'].includes(status),
          }"
          :name="status"
        />
      </div>
      <div class="text-[24px] mt-[24px] font-[600] text-[#FFFFFF] md:text-[#000000D9] dark:md:text-[#FFFFFF]">
        {{ title }}
      </div>
      <div v-if="desc" class="text-[16px] md:text-[#000000D9] dark:md:text-[#FFFFFFD9] text-[#FFFFFFD9] mt-[8px]">
        {{ desc }}
      </div>
    </div>
    <Button v-if="buttonTxt" class="hidden md:block" type="primary" size="large" block @click="emit('click')">
      {{ buttonTxt }}
    </Button>
  </div>
</template>
