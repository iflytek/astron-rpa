<script setup lang="ts">
import { isEmpty, isNil } from 'lodash-es'
import { computed } from 'vue'
import { createReusableTemplate } from '@vueuse/core'

import { getFormTypeArray, FORM_ITEM_REGISTER, FormItemRegisterWithType } from './formItems'

const { formItem, formValues, size = 'default' } = defineProps<{
  formItem: RPA.AtomDisplayItem,
  formValues?: Record<string, any>,
  size?: 'default' | 'small'
}>()
const emit = defineEmits<{
  (e: 'update', key: string, value: any): void
}>()

const [DefineTemplate, ReuseTemplate] = createReusableTemplate<{ items: FormItemRegisterWithType[] }>()

const formTypeArray = computed(() => getFormTypeArray(formItem))

// 根据 formTypeArray 输出对应的 component，按照 [addonBefore, prefix, inline, suffix, addonAfter] 的顺序排列后输出
const layout = computed(() => {
  const components = formTypeArray.value.map(type => ({ ...FORM_ITEM_REGISTER[type], type })).filter(it => !isNil(it))
  const addonBefore = components.filter(component => component.position === 'addonBefore')
  const prefix = components.filter(component => component.position === 'prefix')
  const inline = components.filter(component => component.position === 'inline')
  const suffix = components.filter(component => component.position === 'suffix')
  const addonAfter = components.filter(component => component.position === 'addonAfter')
  const input = [...prefix, ...inline, ...suffix]
  return { addonBefore, input, addonAfter }
})

function handleUpdateValue(key: string, value: any) {
  emit('update', key, value)
}
</script>

<template>
  <div class="form-item-container w-full flex gap-3 items-center" :class="[`form-item-container__${size}`]">
    <DefineTemplate v-slot="{ items }">
      <component
        v-for="item in items"
        :key="item.type"
        :is="item.component" 
        :item="formItem"
        :values="formValues"
        @update="handleUpdateValue"
      />
    </DefineTemplate>

    <div v-if="!isEmpty(layout.addonBefore)" class="flex items-center gap-3" :class="{ 'flex-1': isEmpty(layout.input) }">
      <ReuseTemplate :items="layout.addonBefore" />
    </div>
    <div
      v-if="!isEmpty(layout.input)"
      class="rounded-lg overflow-hidden panel-bg editor-container flex items-center flex-1 gap-2 text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]"
      :class="!isEmpty(formItem.errors) ? 'tip-required' : 'active-container'"
    >
      <ReuseTemplate :items="layout.input" />
    </div>
    <div v-if="!isEmpty(layout.addonAfter)" class="flex items-center gap-3" :class="{ 'flex-1': isEmpty(layout.input) }">
      <ReuseTemplate :items="layout.addonAfter" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.form-item-container {
  .editor-container {
    position: relative;
    padding: 5px 11px;
    font-size: 14px;
    line-height: 22px;
  }

  .active-container {
    &:hover {
      border-color: var(--menuItemFontColor);
    }
  }

  .tip-required {
    border-color: $color-error;
  }
}

.form-item-container__small {
  .editor-container {
    padding: 1px 7px;
  }
}
</style>
