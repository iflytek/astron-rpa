<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { onClickOutside } from '@vueuse/core'
import { Drawer, Spin } from 'ant-design-vue'
import { ref, useTemplateRef } from 'vue'

import AtomForm from './AtomForm.vue'

const props = defineProps<{ clickOutsideIgnoreSelector?: string }>()

const modal = NiceModal.useModal()
const container = useTemplateRef('container')

onClickOutside(container, () => modal.hide(), {
  ignore: props.clickOutsideIgnoreSelector
    ? [`.${props.clickOutsideIgnoreSelector}`]
    : [],
})

const modalWidth = ref(355)

function toggleWidth(wide: boolean) {
  modalWidth.value = wide ? 655 : 355
}
</script>

<template>
  <Drawer
    v-bind="NiceModal.antdDrawer(modal)"
    :width="modalWidth"
    :mask="false"
    :header-style="{ display: 'none' }"
    :content-wrapper-style="{
      margin: 0,
      top: '88px',
      boxShadow: '-3px 0 6px -4px rgba(0, 0, 0, 0.12)',
    }"
    :style="{ borderRadius: '6px' }"
    :body-style="{ padding: 0 }"
  >
    <div ref="container" class="h-full overflow-hidden">
      <div class="px-4 py-3 flex flex-col h-full overflow-hidden">
        <div class="mb-2 text-[14px]">
          {{ $t("components.customComponentSetting") }}
        </div>
        <AtomForm @toggle-width="toggleWidth" />
      </div>
      <div v-if="false" class="flex items-center justify-center min-h-[60vh]">
        <Spin />
      </div>
    </div>
  </Drawer>
</template>
