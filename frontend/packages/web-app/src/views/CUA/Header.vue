<script lang="ts" setup>
import { FlickerMotion } from '@rpa/components'

const props = defineProps<{ isStreaming: boolean, isExpanded: boolean }>();
const emit = defineEmits(["toggleExpanded", "pause"]);

function handleToggleExpanded() {
  emit('toggleExpanded')
}

function handlePause() {
  emit('pause')
}
</script>

<template>
  <div class="flex items-center gap-2 h-8">
    <FlickerMotion v-if="props.isStreaming" />
    <rpa-icon v-else name="success" class="text-base" />

    <div class="text-base font-semibold truncate flex-1">Agent操作中</div>

    <template v-if="props.isStreaming">
      <div class="w-8 h-8 flex items-center justify-center">
        <rpa-hint-icon
          name="square"
          class="text-base"
          enable-hover-bg
          @click="handlePause"
        />
      </div>
      <a-divider type="vertical" class="h-4 m-0" />
    </template>

    <div class="w-8 h-8 flex items-center justify-center">
      <rpa-hint-icon
        :name="props.isExpanded ? 'close-1' : 'maximize'"
        class="text-base"
        enable-hover-bg
        @click="handleToggleExpanded"
      />
    </div>
  </div>
</template>
