<script lang="ts" setup>
import { PauseCircleOutlined, PlayCircleOutlined } from '@ant-design/icons-vue'
import { Button, Empty } from 'ant-design-vue'
import { storeToRefs } from 'pinia'
import { toValue } from 'vue'

import ConfigProvider from '@/components/ConfigProvider/index.vue'
import Header from '@/components/Header.vue'
import { RecordActionMap } from '@/constants/record'

import { useRecordStore } from './store'
import { emitToMain } from './utils'

const recordStore = useRecordStore()
const { isRecording, list, canRedo, canUndo } = storeToRefs(recordStore)

function handleClose() {
  recordStore.stopRecord()
  emitToMain('close')
}

function handleSubmit() {
  emitToMain('save', toValue(list))
  handleClose()
}
</script>

<template>
  <ConfigProvider>
    <div class="p-4 h-screen">
      <div
        class="h-full bg-bg-elevated rounded-lg shadow-lg flex flex-col gap-3 overflow-hidden"
      >
        <Header
          class="!relative"
          :title="$t('smartRecording')"
          :minimize="false"
          :maximize="false"
          :close-fn="handleClose"
          :dbtoggle-prevent="true"
        />

        <div class="px-3 flex gap-1 items-center">
          <Button
            size="small"
            class="!h-[26px] !text-xs !px-2 flex items-center mr-1"
            @click="recordStore.toggleRecord"
          >
            <component
              :is="isRecording ? PauseCircleOutlined : PlayCircleOutlined"
              size="16"
            />
            <span>{{ isRecording ? "暂停录制[ESC]" : "开始录制[F4]" }}</span>
          </Button>

          <rpa-hint-icon
            name="tools-undo"
            title="撤销"
            enable-hover-bg
            :disabled="!canUndo"
            @click="recordStore.undo"
          />
          <rpa-hint-icon
            name="tools-recover"
            title="重做"
            enable-hover-bg
            :disabled="!canRedo"
            @click="recordStore.redo"
          />
        </div>

        <div
          class="flex-1 mx-3 rounded border border-border-secondary flex flex-col justify-center items-center overflow-hidden"
        >
          <template v-if="list.length > 0">
            <div class="flex-1 w-full overflow-y-auto">
              <div
                v-for="(item, index) in list"
                :key="item.action"
                class="flex items-center p-2 gap-2 border-b border-border-secondary text-[13px] group"
              >
                <rpa-icon :name="RecordActionMap[item.action].icon" />
                <span class="flex-1">
                  {{ RecordActionMap[item.action].label }}
                  <span
                    v-if="item.name"
                    class="text-xs text-text-secondary px-1"
                  >
                    {{ item.name }}
                  </span>
                </span>
                <span
                  class="invisible group-hover:visible cursor-pointer rounded-lg hover:bg-fill-secondary p-[1px]"
                  @click="recordStore.clear(index)"
                >
                  <rpa-icon name="close" />
                </span>
              </div>
            </div>

            <div class="w-full pt-1">
              <rpa-hint-icon
                name="atom-delete"
                enable-hover-bg
                class="text-xs"
                size="14"
                @click="recordStore.clearAll"
              >
                <template #suffix>
                  <span class="pl-1">清空</span>
                </template>
              </rpa-hint-icon>
            </div>
          </template>
          <Empty v-else :image="Empty.PRESENTED_IMAGE_SIMPLE">
            <template v-if="isRecording" #description>
              请在桌面或软件中开始操作
            </template>
            <template v-else #description>
              <div>点击上方“开始录制”</div>
              <div>星辰RPA会记录你的操作，智能生成流程</div>
            </template>
          </Empty>
        </div>

        <div class="flex justify-end pb-4 px-3">
          <Button type="primary" @click="handleSubmit">
            完成
          </Button>
        </div>
      </div>
    </div>
  </ConfigProvider>
</template>
