<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Drawer, Segmented } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, ref } from 'vue'

import BasicContent from './BasicContent.vue'
import { useProvideBasicStore } from './basicStore'
import RecordContent from './RecordContent.vue'

const props = defineProps<{ robotId: string, version: number }>()

const modal = NiceModal.useModal()

const { t } = useTranslation()
const currentTab = ref('info')

const tabs = computed(() => [
  {
    label: t('basicInformation'),
    value: 'info',
  },
  {
    label: t('executionRecords'),
    value: 'record',
  },
])

useProvideBasicStore(props.robotId)
</script>

<template>
  <Drawer
    v-bind="NiceModal.antdDrawer(modal)"
    :title="$t('appDetails')"
    class="robotDetailsModal"
    placement="right"
    :width="628"
    :footer="null"
  >
    <div class="h-full flex flex-col">
      <Segmented v-model:value="currentTab" block :options="tabs" />
      <div class="mt-4 flex-1 overflow-auto">
        <BasicContent v-if="currentTab === 'info'" />
        <RecordContent v-else :robot-id="props.robotId" :version="props.version" />
      </div>
    </div>
  </Drawer>
</template>

<style lang="scss">
.robotDetailsModal {
  .ant-modal-body {
    height: 560px;
    overflow-x: hidden;
    overflow-y: auto;
  }
  .ant-drawer-body {
    padding-top: 18px;
    &::-webkit-scrollbar {
      width: 0;
    }
  }
}
</style>
