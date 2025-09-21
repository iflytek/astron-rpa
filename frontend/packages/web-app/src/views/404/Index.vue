<script lang="ts" setup>
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import Header from '@/components/Header.vue'
</script>

<template>
  <ConfigProvider>
    <div class="error">
      <Header :maximize="false" class="error-header" />
      <div class="error-container">
        <p class="text-xl mt-[80px]">
          当前网络无法连接，请关闭后重试
        </p>
      </div>
    </div>
  </ConfigProvider>
</template>

<style>
.error-header {
  --headerBgColor: #2c69ff;
  --headerFontColor: #d3e0ff;
  --headerTitleColor: #ffffff;
  --headerFontColorHover: #ffffff;
  --headerHeight: 48px;
  box-shadow: 0 1px 3px 0 hsl(0deg 0% 84% / 50%);
  width: 100%;
}

.error-container {
  padding-top: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}
</style>
