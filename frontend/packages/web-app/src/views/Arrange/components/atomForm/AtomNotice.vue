<script setup lang="ts">
import { useFormStore } from "./hooks/useFormStore";

const { atom } = useFormStore();
</script>

<template>
  <div
    v-if="atom.notices === 'ai_notices'"
    class="p-3 text-primary text-[13px] leading-[1.6] truncate rounded-xl bg-[rgba(215,215,255,0.40)]"
  >
    AI可能误判，运行和调试将消耗积分，优先消耗赠送额度。
  </div>
</template>
