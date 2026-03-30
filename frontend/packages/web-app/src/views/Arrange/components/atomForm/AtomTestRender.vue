<script setup lang="ts">
import { isEmpty } from 'lodash-es'

import ChainOfThought from '@/components/ChainOfThought/ChainOfThought.vue'
import { useFormStore } from "./hooks/useFormStore";

const { chainOfThoughtSteps: steps } = useFormStore();
</script>

<template>
  <ChainOfThought
    :steps="steps"
    class="h-full"
    :class="{'flex items-center justify-center': isEmpty(steps)}"
  >
    <template #empty>
      <div class="text-center text-text-tertiary">
        <rpa-icon name="noresult" class="text-[32px]" />
        <div class="leading-[22px] mt-1">暂无数据</div>
      </div>
    </template>
  </ChainOfThought>
</template>
