<script setup lang="ts">
import { Tabs, TabPane } from 'ant-design-vue'
import { ref } from 'vue'

import LinkInvite from '@/views/Home/components/TeamMarket/MarketManage/LinkInvite.vue'
import PhoneInvite from '@/views/Home/components/TeamMarket/MarketManage/PhoneInvite.vue'
import { useUserStore } from '@/stores/useUserStore'

const { marketId } = defineProps({
  marketId: {
    type: String,
    default: '',
  },
  users: {
    type: Array,
    default: () => [],
  },
})

const userStore = useUserStore()
const addTypesMap = {
  personal: ['link'],
  professional: ['link', 'phone'],
  enterprise: ['phone']
}
const addTypes = addTypesMap[userStore.currentTenant?.tenantType]
const activeTab = ref(addTypes[0])
const emit = defineEmits(['change', 'inviteTypeChange', 'linkChange'])

</script>

<template>
  <div class="modal-form invite-user-modal">
    <Tabs type="card" size="small" v-if="addTypes?.length > 1" v-model:active-key="activeTab" @change="(key) => emit('inviteTypeChange', key)">
      <TabPane key="add" tab="直接添加" />
      <TabPane key="link" tab="邀请链接" />
    </Tabs>
    <LinkInvite v-if="activeTab === 'link'" :market-id="marketId" @link-change="(link: string) => emit('linkChange', link)"/>
    <PhoneInvite v-if="activeTab === 'add'" :market-id="marketId" :selected-users="users" @change="(userList: any[]) => emit('change', userList)"/>
  </div>
</template>

<style lang="scss">
.invite-user-modal{
  .ant-modal-confirm-content {
    width: 100%!important;
    max-width: 100%!important;
  }

  .ant-tabs-nav-wrap, .ant-tabs-nav-list {
    width: 100%;
    border-radius: 8px;
    .ant-tabs-tab {
      width: 50%;
    }
  }
  .ant-tabs >.ant-tabs-nav{
    margin-bottom: 24px;
    &:before {
      display: none;
    }
  }
  .ant-tabs-content-holder{
    height: 100%;
  }
  .ant-tabs-content{
    height: 100%;
  }
  .ant-tabs-nav-list{
    background-color: #ECEDF4;
    border: none;
    border-radius: 8px!important;
    padding: 3px;
    
    .ant-tabs-tab {
      border: none;
      border-radius: 6px!important;
      text-align: center;
      background: transparent;
      .ant-tabs-tab-btn {
        width: 100%;
        color: #000000A6;
      }
      &.ant-tabs-tab-active {
        background-color: #FFFFFF;
        box-shadow: none;
        .ant-tabs-tab-btn {
          color: #000000D9;
        }
      }
    }
  }
}
.dark .invite-user-modal{
  .ant-tabs-nav-list{
    background-color: #141414;
    padding: 3px 3px 2px;
    .ant-tabs-tab {
      .ant-tabs-tab-btn {
        color: #FFFFFFA6;
      }
      &.ant-tabs-tab-active {
        background-color: #FFFFFF1F;
        box-shadow: 0px -1px 0px 0px rgba(255, 255, 255, 0.3);
        .ant-tabs-tab-btn {
          color: #FFFFFFD9;
        }
      }
    }
  }
}
</style>
