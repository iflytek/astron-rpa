<script setup lang="ts">
import { NodeViewContent, nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'

defineProps(nodeViewProps)
</script>

<template>
  <NodeViewWrapper
    class="inline-flex mx-1 px-1 bg-[#D7D7FF]/[.4] dark:bg-[#5D59FF]/[.35] text-[#5D59FF]/[.35] dark:text-[#8482FE]/[.9] border rounded-lg"
    :class="{ 'border-transparent': !selected }"
  >
    <span :contenteditable="false">[</span>
    <NodeViewContent />
    <span :contenteditable="false">]</span>
  </NodeViewWrapper>
</template>
