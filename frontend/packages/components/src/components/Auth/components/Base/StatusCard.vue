<script setup lang="ts">
import { Button } from 'ant-design-vue'

interface Props {
  title: string
  desc?: string
  buttonTxt?: string
}

withDefaults(defineProps<Props>(), {})

const emit = defineEmits<{
  click: []
}>()

</script>

<template>
  <div class="status-card bg-[#ffffff] dark:bg-[#000000] shadow-lg rounded-[16px] w-[400px] h-[auto] p-[40px]">
    <div class="text-center text-[20px] mt-[10px] font-[600] dark:text-[#FFFFFF]">{{title}}</div>
    <div class="text-[14px] text-[#00000073] dark:text-[#FFFFFF73] my-[20px]" v-if="desc">{{desc}}</div>
    <Button v-if="buttonTxt" type="primary" class="" block @click="emit('click')">
      {{buttonTxt}}
    </Button>
  </div>
</template>
