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
  <div class="status-card bg-[#ffffff] dark:bg-[#000000] shadow-lg rounded-[16px] w-[400px] h-full p-[40px] text-center ">
    <div class="my-[40px]" :class="!buttonTxt ? 'mt-[80px]' : ''">
      <RpaIcon
        class="inline-block w-[320px] h-[160px]"
        :name="status"
      />
      <div class="text-[24px] mt-[24px] font-[600] dark:text-[#FFFFFF]">
        {{ title }}
      </div>
      <div v-if="desc" class="text-[16px] text-[#000000D9] dark:text-[#FFFFFF73] mt-[8px]">
        {{ desc }}
      </div>
    </div>
    <Button v-if="buttonTxt" type="primary" size="large" block @click="emit('click')">
      {{ buttonTxt }}
    </Button>
  </div>
</template>
