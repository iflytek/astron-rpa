<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Divider, message, Space } from 'ant-design-vue'
import { defineComponent, ref } from 'vue'

import { deployApp, unDeployUserList } from '@/api/market'
import type { resOption } from '@/views/Home/types'

import type { cardAppItem } from '../../types/market'

import DeployedAccountsTable from './DeployedAccountsTable.vue'

const props = defineProps<{ record: cardAppItem }>()

const modal = NiceModal.useModal()

const confirmLoading = ref(false)
const searchText = ref('')
const userIds = ref([])
const isAll = ref(false)
const accountsOptions = ref([])
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

function getMembersByTeam() {
  unDeployUserList({
    marketId: props.record.marketId,
    appId: props.record.appId,
    phone: searchText.value,
  }).then((res: resOption) => {
    const { data } = res
    if (data) {
      const ownerList = data.map((i) => {
        return {
          name: `${i.realName || '--'}(${i.phone || '--'})`,
          userId: i.creatorId,
        }
      })
      accountsOptions.value = ownerList
    }
  })
}

getMembersByTeam()

async function handleOk() {
  if (userIds.value.length === 0) {
    message.warning('请选择账号')
    return
  }

  confirmLoading.value = true
  const { marketId, appId, appName } = props.record
  await deployApp({ marketId, appId, appName, userIdList: userIds.value })
  confirmLoading.value = false

  message.success('部署成功')
  modal.hide()
}

function handleChange() {
  userIds.value = []
  if (isAll.value) {
    userIds.value = accountsOptions.value.filter(i => i.name.toLowerCase().includes(searchText.value.toLowerCase())).map(i => i.userId)
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
    title="部署机器人"
    :confirm-loading="confirmLoading"
    ok-text="确认部署"
    :width="600"
    centered
    @ok="handleOk"
  >
    <div class="deploy-robot-modal">
      <DeployedAccountsTable :allow-select="false" :record="props.record" />
      <div class="select-user">
        <div class="title">
          新增账号
        </div>
        <a-select
          v-model:value="userIds"
          placeholder="请输入新增账号"
          mode="multiple"
          allow-clear
          auto-clear-search-value
          style="width: 100%;margin-top: 10px;"
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
                全选
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
