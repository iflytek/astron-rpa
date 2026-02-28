<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'
import { Divider, message, Space } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { defineComponent, ref } from 'vue'

import { deployApp, unDeployUserList } from '@/api/market'

import type { cardAppItem } from '../../types/market'

import DeployedAccountsTable from './DeployedAccountsTable.vue'

const props = defineProps<{ record: cardAppItem }>()

const modal = NiceModal.useModal()
const { t } = useTranslation()

const confirmLoading = ref(false)
const searchText = ref('')
const userIds = ref([])
const isAll = ref(false)

const VNodes = defineComponent({
  props: {
    vnodes: {
      type: Object,
      required: true,
    },
  },
  render() {
    return this.vnodes
  },
})

const { state: accountsOptions, execute: getMembersByTeam } = useAsyncState(
  () =>
    unDeployUserList({
      marketId: props.record.marketId,
      appId: props.record.appId,
      phone: searchText.value,
    }).then((data = []) =>
      data.map(i => ({
        name: `${i.realName || '--'}(${i.phone || '--'})`,
        userId: i.creatorId,
      })),
    ),
  [],
  { resetOnExecute: false },
)

async function handleOk() {
  if (userIds.value.length === 0) {
    message.warning(t('common.selectAccount'))
    return
  }

  confirmLoading.value = true
  const { marketId, appId, appName } = props.record
  await deployApp({ marketId, appId, appName, userIdList: userIds.value })
  confirmLoading.value = false

  message.success(t('common.deploySuccess'))
  modal.hide()
}

function handleChange() {
  userIds.value = []
  if (isAll.value) {
    userIds.value = accountsOptions.value
      .filter(i =>
        i.name.toLowerCase().includes(searchText.value.toLowerCase()),
      )
      .map(i => i.userId)
  }
}
function handleSelectChange(value: string) {
  console.log('value', value)
  if (userIds.value.length === 0) {
    isAll.value = false
  }
}
function handleSearch(value: string) {
  searchText.value = value
  getMembersByTeam()
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('market.deployApp')"
    :confirm-loading="confirmLoading"
    :ok-text="$t('market.confirmDeploy')"
    :width="600"
    centered
    @ok="handleOk"
  >
    <div class="deploy-robot-modal">
      <DeployedAccountsTable :allow-select="false" :record="props.record" />
      <div class="select-user">
        <div class="title">
          {{ $t('market.addAccount') }}
        </div>
        <a-select
          v-model:value="userIds"
          :placeholder="$t('market.enterAddAccount')"
          mode="multiple"
          allow-clear
          auto-clear-search-value
          style="width: 100%; margin-top: 10px"
          show-search
          :field-names="{ label: 'name', value: 'userId' }"
          :filter-option="false"
          :not-found-content="null"
          :options="accountsOptions"
          @change="handleSelectChange"
          @search="handleSearch"
        >
          <template #dropdownRender="{ menuNode: menu }">
            <VNodes :vnodes="menu" />
            <Divider style="margin: 4px 0" />
            <Space style="padding: 4px 8px">
              <a-checkbox v-model:checked="isAll" @change="handleChange">
                {{ $t('selectAll') }}
              </a-checkbox>
            </Space>
          </template>
        </a-select>
      </div>
    </div>
  </a-modal>
</template>

<style lang="scss" scoped>
.title {
  color: initial;
  font-weight: bold;
  font-size: 14px;
}
</style>
