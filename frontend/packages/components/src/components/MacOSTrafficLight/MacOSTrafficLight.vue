<script setup lang="ts">
const props = defineProps<{
  close?: boolean
  minimize?: boolean
  maximize?: boolean
  isMaximized?: boolean
}>()

const emit = defineEmits<{
  close: []
  minimize: []
  maximize: []
}>()
</script>

<template>
  <div class="mac-traffic-light group">
    <button
      v-if="props.close !== false"
      class="mac-btn mac-btn--close text-[#EC6A5E] active:text-[#F09389]"
      title="关闭"
      @click="emit('close')"
    >
      <svg width="12" height="12" viewBox="0 0 85.4 85.4" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M42.7 85.4C66.3 85.4 85.4 66.3 85.4 42.7C85.4 19.1 66.3 0 42.7 0C19.1 0 0 19.1 0 42.7C0 66.3 19.1 85.4 42.7 85.4Z" fill="currentColor"/>
        <path fill-rule="evenodd" clip-rule="evenodd" d="M42.7 81.8C64.3 81.8 81.8 64.3 81.8 42.7C81.8 21.1 64.3 3.59998 42.7 3.59998C21.1 3.59998 3.59998 21.1 3.59998 42.7C3.59998 64.3 21.1 81.8 42.7 81.8Z" fill="currentColor"/>
        <!-- hover icon path -->
        <g class="hidden group-hover:block">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M22.5 57.7999L57.7999 22.5C59.1999 21.1 61.3999 21.1 62.7999 22.5L62.9 22.6C64.3 24 64.3 26.2 62.9 27.6L27.6 62.9C26.2 64.3 24 64.3 22.6 62.9L22.5 62.7999C21.1 61.3999 21.1 59.0999 22.5 57.7999Z" fill="#8B1A0F"/>
          <path fill-rule="evenodd" clip-rule="evenodd" d="M27.5 22.5L62.8 57.7999C64.2 59.1999 64.2 61.3999 62.8 62.7999L62.7 62.9C61.3 64.3 59.1 64.3 57.7 62.9L22.4 27.6C21 26.2 21 24 22.4 22.6L22.5 22.5C23.9 21.1 26.2 21.1 27.5 22.5Z" fill="#8B1A0F"/>
        </g>
      </svg>
    </button>

    <button
      v-if="props.minimize !== false"
      class="mac-btn mac-btn--minimize text-[#F4BF4F] active:text-[#FBEB74]"
      title="最小化"
      @click="emit('minimize')"
    >
      <svg width="12" height="12" viewBox="0 0 85.4 85.4" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M42.7 85.4C66.3 85.4 85.4 66.3 85.4 42.7C85.4 19.1 66.3 0 42.7 0C19.1 0 0 19.1 0 42.7C0 66.3 19.1 85.4 42.7 85.4Z" fill="currentColor"/>
        <path fill-rule="evenodd" clip-rule="evenodd" d="M42.7 81.8C64.3 81.8 81.8 64.3 81.8 42.7C81.8 21.1 64.3 3.59998 42.7 3.59998C21.1 3.59998 3.59998 21.1 3.59998 42.7C3.59998 64.3 21.1 81.8 42.7 81.8Z" fill="currentColor"/>
        <!-- hover icon path -->
        <g class="hidden group-hover:block">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M17.7 39.1H67.5999C69.4999 39.1 71.0999 40.7 71.0999 42.6V42.7C71.0999 44.6 69.4999 46.2 67.5999 46.2H17.7C15.8 46.2 14.2 44.6 14.2 42.7V42.6C14.2 40.7 15.8 39.1 17.7 39.1Z" fill="#A87229"/>
        </g>
      </svg>
    </button>

    <button
      v-if="props.maximize !== false"
      class="mac-btn mac-btn--maximize text-[#62C554] active:text-[#86F37E]"
      :title="isMaximized ? '还原' : '最大化'"
      @click="emit('maximize')"
    >
      <svg width="12" height="12" viewBox="0 0 85.4 85.4" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M42.7 85.4C66.3 85.4 85.4 66.3 85.4 42.7C85.4 19.1 66.3 0 42.7 0C19.1 0 0 19.1 0 42.7C0 66.3 19.1 85.4 42.7 85.4Z" fill="currentColor"/>
        <path fill-rule="evenodd" clip-rule="evenodd" d="M42.7 81.8C64.3 81.8 81.8 64.3 81.8 42.7C81.8 21.1 64.3 3.59998 42.7 3.59998C21.1 3.59998 3.59998 21.1 3.59998 42.7C3.59998 64.3 21.1 81.8 42.7 81.8Z" fill="currentColor"/>
        <!-- hover icon path -->
        <g class="hidden group-hover:block">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M31.2 20.8H57.9C61.5 20.8 64.4 23.7 64.4 27.3V54L31.2 20.8ZM54.4 64.5H27.6C24 64.5 21.1 61.6 21.1 58V31.2001L54.4 64.5Z" fill="#286017"/>
        </g>
      </svg>
    </button>
  </div>
</template>

<style scoped>
.mac-traffic-light {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mac-btn {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: none;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  flex-shrink: 0;
}
</style>
