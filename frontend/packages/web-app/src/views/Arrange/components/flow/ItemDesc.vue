<script setup lang="ts">
import type { PropType } from 'vue'

import RenderFormItem from '@/views/Arrange/components/descForm/RenderFormItem.vue'
import { decodeHtml } from '@/views/Arrange/utils/index'
import { renderAtomRemark } from '@/views/Arrange/utils/renderAtomRemark'

const { item } = defineProps({
  item: {
    type: Object as PropType<RPA.Atom>,
  },
  canEdit: {
    type: Boolean,
    default: true,
  },
  flowId: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="desc textHidden text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65]">
    <template
      v-for="(result, idx) in renderAtomRemark(item)"
      :key="item.id + idx"
    >
      <template v-if="result.variable && result.currentItem">
        <RenderFormItem :id="item.id" :can-edit="canEdit" :form-item="result.currentItem" :desc="decodeHtml(result.sr[2])" />
      </template>
      <template v-else>
        <span>{{ result }}</span>
      </template>
    </template>
  </div>
</template>
