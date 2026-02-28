<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'
import { Empty, message, Spin } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

import { getPushHistoryVersions, pushApp } from '@/api/market'

import type { cardAppItem } from '../../types/market'

import DeployedAccountsTable from './DeployedAccountsTable.vue'

const props = defineProps<{ record: cardAppItem }>()
const { appId, marketId } = props.record

const modal = NiceModal.useModal()
const confirmLoading = ref(false)
const selectedVersion = ref('')
const selectedIds = ref([])
const { t } = useTranslation()

const { state: versionList, isLoading: spinning } = useAsyncState(() => getPushHistoryVersions({ appId, marketId }), [])

async function handleOk() {
  if (!selectedIds.value.length) {
    message.warning(t('common.selectAccount'))
    return
  }

  if (!selectedVersion.value) {
    message.warning(t('versionSelect'))
    return
  }

  confirmLoading.value = true
  await pushApp({
    marketId: props.record.marketId,
    appId: props.record.appId,
    userIdList: selectedIds.value,
    appVersion: selectedVersion.value,
  })
  confirmLoading.value = false

  message.success(t('market.versionPushSuccess'))
  modal.hide()
}

function getSelectedIds(ids: string[]) {
  selectedIds.value = ids
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('market.versionPush')"
    :confirm-loading="confirmLoading"
    :ok-text="$t('market.confirmPush')"
    :width="600"
    centered
    @ok="handleOk"
  >
    <div class="version-push-modal">
      <DeployedAccountsTable :allow-select="true" :record="props.record" @selected-ids="getSelectedIds" />
      <div class="version-list">
        <div class="title mb-4">
          {{ $t('versionSelect') }}
        </div>
        <div v-if="spinning" class="version-spinning">
          <Spin />
        </div>
        <div v-else class="version-content">
          <a-radio-group v-if="versionList?.length" v-model:value="selectedVersion" class="flex flex-col">
            <a-radio v-for="version in versionList" :key="version.version" class="p-4 border border-primary rounded-lg" :value="version.version">
              <div class="version-item">
                <div class="version-header">
                  <div>{{ $t('versionWithNumber', { version: version.version }) }}</div>
                  <div class="ml-[300px]">
                    {{ version.createTime }}
                  </div>
                </div>
                <div class="version-description">
                  {{ version.updateLog }}
                </div>
              </div>
            </a-radio>
          </a-radio-group>
          <Empty v-else />
        </div>
      </div>
    </div>
  </a-modal>
</template>

<style lang="scss">
.version-push-modal {
  .version-list {
    width: 550px;
    height: 180px;
    .version-spinning {
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .version-content {
      width: 100%;
      max-height: 130px;
      overflow: hidden;
      overflow-y: auto;
      .version-item {
        margin-left: 4px;
        width: 100%;
        height: 44px;
        white-space: nowrap;
        // padding: 5px;
        .version-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .version-description {
          width: 100%;
          max-height: 60px;
          color: #aaa;
        }
      }
    }
  }
}
.title {
  color: initial;
  font-weight: bold;
  font-size: 14px;
}
</style>
