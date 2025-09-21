<script setup lang="ts">
import DiffuseDark from '@/components/Illustration/DiffuseDark.vue'
import DiffuseLight from '@/components/Illustration/DiffuseLight.vue'
import RobotIll1ustration from '@/components/Illustration/Robot1.vue'
import RobotIll2ustration from '@/components/Illustration/Robot2.vue'
import { useAppConfigStore } from '@/stores/useAppConfig'

const props = defineProps<{
  illustration?: Illustration
}>()

const { isDark } = useAppConfigStore()

export type Illustration = 'robot1' | 'robot2'
</script>

<template>
  <div class="bg-illustration h-[400px]">
    <DiffuseDark v-if="isDark" height="100%" class="absolute right-0" />
    <DiffuseLight v-else height="100%" class="absolute right-0" />

    <RobotIll1ustration
      v-if="props.illustration === 'robot1'"
      class="short:w-[350px] short:h-[240px] absolute top-[44px] short:top-[16px] right-[56px] z-0"
    />
    <RobotIll2ustration
      v-if="props.illustration === 'robot2'"
      class="short:w-[350px] short:h-[240px] absolute top-[14px] right-[56px] z-0"
    />
  </div>
</template>

<style scoped>
.bg-illustration {
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
}
</style>
