<script lang="ts" setup>
import { PlusCircleOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'

import { ProcessModal } from '@/views/Arrange/components/process'

defineProps({
  btnType: {
    type: String,
    default: 'text', // icon-按钮仅展示icon,  text-按钮展示icon+文字，
  },
  showCloud: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['click'])

function addProcess() {
  NiceModal.show(ProcessModal, { type: 'process' })
  emit('click')
}
</script>

<template>
  <span
    class="process-add-btn inline-flex items-center justify-center cursor-pointer"
    :class="`process-add-btn_${btnType}`"
    @click="addProcess"
  >
    <a-tooltip v-if="btnType === 'icon'" title="新建子流程" placement="bottom">
      <PlusOutlined class="inline-block" />
    </a-tooltip>
    <template v-else>
      <PlusCircleOutlined class="icon" />
      <span class="text">新建子流程</span>
    </template>
  </span>
</template>

<style lang="scss" scoped>
.process-add-btn {
  background: #ffffff;
  border-left: 1px solid #f9f9f9;
  border: 0;
  width: 35px;
  height: 32px;
  line-height: 30px;
  &:hover {
    color: $color-primary;
  }
  :deep(.anticon) {
    font-size: 14px;
  }
  &_text {
    width: 100%;
    .icon {
      color: $color-primary;
    }
    .text {
      font-size: 12px;
      margin-left: 5px;
    }
  }
}
</style>
