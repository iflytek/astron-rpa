/** 使用场景：「发送邮件-内容」 */
<script setup lang="ts">
import { getHTMLClip } from '@/api/resource'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emit = defineEmits<FormItemEmits>()

const handleClick = async () => {
  // 这里的 is_html 来源于表单中的另一项「是否为HTML格式」
  const is_html = props.values?.['is_html'] ?? false
  const res = await getHTMLClip({ is_html })
  const content = res.data.content
  
  if (content) {
    emit('update', props.item.key, content)
  }
}
</script>

<template>
  <a-button
    type="link"
    class="panel-bg rounded-lg w-[30px] h-[32px] flex items-center justify-center text-inherit"
    @click="handleClick"
  >
    <template #icon>
      <rpa-hint-icon title="填充内容" size="14" name="bottom-pick-menu-create" />
    </template>
  </a-button>
</template>
