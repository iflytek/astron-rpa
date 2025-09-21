<script lang="ts" setup>
defineProps<{ colorList: Array<string> }>()

const modelValue = defineModel('value', { type: String, required: true })

function handleClick(color: string) {
  modelValue.value = color
}
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <div
      v-for="color in colorList"
      :style="{ background: color }"
      :class="{ border: modelValue === color }"
      class="flex justify-center items-center w-6 h-6 rounded-[6px] border-[#000000]/[.65] dark:border-[#FFFFFF]/[.65] cursor-pointer"
      @click="handleClick(color)"
    >
      <rpa-hint-icon v-if="modelValue === color" name="check" />
    </div>
  </div>
</template>
