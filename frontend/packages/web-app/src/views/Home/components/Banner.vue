<script setup lang="ts">
const props = defineProps<{
  title: string
  subTitle: string
  actionText?: string
}>()

const emit = defineEmits<{
  (e: 'action'): void
}>()
</script>

<template>
  <div
    class="banner w-full h-[259px] short:h-[190px] flex justify-between items-center"
  >
    <div class="flex flex-col items-start justify-center pl-5">
      <div class="banner-title">
        {{ props.title }}
      </div>

      <div class="banner-sub-title text-[rgba(0,0,0,0.65)] dark:text-white">
        {{ props.subTitle }}
      </div>

      <a-button
        v-if="actionText"
        type="primary"
        size="large"
        class="banner-button"
        @click="emit('action')"
      >
        {{ actionText }}
      </a-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.banner {
  .banner-title {
    font-size: 32px;
    font-weight: 500;
    line-height: 45px;
    margin-bottom: 8px;
  }

  .banner-sub-title {
    font-size: 15px;
    line-height: 21px;
  }

  .banner-button {
    margin-top: 24px;
    background: linear-gradient(270deg, #4f4bff 0%, #3f75ff);
  }
}
</style>
