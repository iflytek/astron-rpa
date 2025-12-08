<script setup lang="ts">
import LaunchCarousel from '../../../LaunchCarousel/LaunchCarousel.vue';
import LoginBg from '../../assets/imgs/login_bg.png'
import PageHeader from './PageHeader.vue'

</script>

<template>
  <div class="auth-container w-full h-full flex items-center justify-center bg-[#F4F4FF] dark:bg-[#141414]" :class="[colorTheme]" :style="{ backgroundImage: `url(${LoginBg})`, backgroundSize: '100% 100%' }">
    <PageHeader />
    <div class="flex items-center justify-between w-[920px] h-[540px]">
      <div class="text-[#000000D9] dark:text-[#FFFFFF] ">
        <div class="w-[400px] px-[20px] mb-[40px] flex flex-col items-center justify-center text-[32px] text-left">
          <div class="w-full"><span class="text-[#726FFF]">星辰RPA,</span>让重复自动化</div>
          <div class="w-full">让决策更智能</div>
         </div>
        <LaunchCarousel />
      </div>
      <slot></slot>
    </div>
  </div>
</template>