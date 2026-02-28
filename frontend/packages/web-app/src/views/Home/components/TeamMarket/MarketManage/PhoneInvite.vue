<script setup lang="ts">
import { Empty, Select, Table } from 'ant-design-vue'

import { usePhoneInvite } from '@/views/Home/components/TeamMarket/hooks/MarketManage/useInviteUser.tsx'
import RoleDropdown from '@/views/Home/components/TeamMarket/MarketManage/RoleDropdown.vue'

const { marketId } = defineProps({
  marketId: {
    type: String,
    default: '',
  },
  selectedUsers: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['change'])

const { defaultUserType, selectIds, userList, clearUserList, userListByPhone, inviteUsersTableColumns, allSelectUsers, selectData, keyDownChange, changeDefaultUserType } = usePhoneInvite(marketId, 'invite', emit)
</script>

<template>
  <div class="modal-form">
    <div class="flex items-center">
      <Select
        v-model:value="selectIds"
        popup-class-name="invite"
        :placeholder="$t('market.enterUserNameOrPhone')"
        style="width: 100%"
        :get-popup-container="(triggerNode) => triggerNode.parentNode"
        show-search
        :show-arrow="false"
        mode="multiple"
        :default-active-first-option="false"
        :filter-option="false"
        option-label-prop="label"
        @search="userListByPhone"
        @change="selectData"
        @blur="clearUserList"
        @input-keydown="keyDownChange"
      >
        <Select.Option v-for="item in userList" :key="item.creatorId" :value="item.creatorId" :label="item.realName">
          <div class="option-item">
            <div class="option-item-value">
              {{ item.realName }}
            </div>
            <div class="option-item-value">
              {{ item.phone }}
            </div>
          </div>
        </Select.Option>
      </Select>
      <RoleDropdown pop-container-type="parent" type="ghost" :user-type="defaultUserType" @change="(userType) => changeDefaultUserType(userType)" />
    </div>
    <div>
      <div v-if="allSelectUsers.length > 0" class="my-[10px]">
        {{ $t('market.selectedMembers', { count: allSelectUsers.length }) }}
      </div>
      <Table
        :columns="inviteUsersTableColumns"
        :data-source="allSelectUsers"
        :show-header="false"
        class="custom-table w-full"
        :pagination="false"
        size="small"
      >
        <template #emptyText>
          <Empty :image="Empty.PRESENTED_IMAGE_SIMPLE" :description="$t('market.searchMembersTip')" />
        </template>
      </Table>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.option-item {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 300px;
  &-value {
    width: 110px;
    margin-right: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
:deep(.ant-select-dropdown) {
  min-height: 200px;
}
:deep(.ant-select-dropdown .ant-select-item) {
  position: initial;
}
:deep(.ant-select-item-option) {
  align-items: center;
}
:deep(.ant-select-item-option .ant-select-item-option-state) {
  font-weight: bold;
}
:deep(ant-select-dropdown-menu-item) {
  overflow: visible;
}
</style>
