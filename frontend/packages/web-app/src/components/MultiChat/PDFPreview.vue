<template>
  <VuePdfEmbed
    ref="pdfRef"
    annotation-layer
    text-layer
    class="h-full"
    :width="width"
    :source="props.source"
  />
</template>

<script setup lang="ts">
import VuePdfEmbed from 'vue-pdf-embed'
import { useElementSize } from '@vueuse/core'
import { useTemplateRef } from 'vue'

import 'vue-pdf-embed/dist/styles/annotationLayer.css'
import 'vue-pdf-embed/dist/styles/textLayer.css'

const props = defineProps<{ source: string | Uint8Array | object }>()

const pdfRef = useTemplateRef('pdfRef')
const { width } = useElementSize(pdfRef)
</script>
