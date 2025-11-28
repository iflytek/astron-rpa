<script setup lang="ts">
import { isString } from 'lodash-es'

import { renderAtomRemark } from './utils/renderAtomRemark'
import RenderFormItem from './descForm/RenderFormItem.vue'
import { useFlowState } from './hooks'

const props = withDefaults(defineProps<{ item: RPA.Atom, canEdit?: boolean, flowId?: string }>(), {
  canEdit: true,
  flowId: '',
})

const { astParser } = useFlowState()
</script>

<template>
  <div class="desc textHidden text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65]">
    <template
      v-for="(result, idx) in renderAtomRemark(props.item, astParser)"
      :key="props.item.id + idx"
    >
      <template v-if="isString(result)">
        {{ result }}
      </template>
      <RenderFormItem
        v-else
        :id="props.item.id"
        :can-edit="props.canEdit"
        :form-item="result.formItem"
        :desc="result.displayValue"
      />
    </template>
  </div>
</template>
