<script setup lang="ts">
import { isArray } from 'lodash-es'
import { ArrowsAltOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'

import { TextareaModal } from '@/views/Arrange/components/tools/components'
import type { FormItemProps } from './index'

const iconStyle = { fontSize: '16px', color: 'inherit' }

const props = defineProps<FormItemProps>()

const hanldeClick = () => {
  const itemDataVal = isArray(props.item.value) ? props.item.value : []

  NiceModal.show(TextareaModal, {
    itemDataVal,
    onOk: (data) => {
      console.log(data)
    },
  })
}
</script>

<template>
  <ArrowsAltOutlined class="cursor-pointer opacity-55" :style="iconStyle" @click="hanldeClick" />
</template>
