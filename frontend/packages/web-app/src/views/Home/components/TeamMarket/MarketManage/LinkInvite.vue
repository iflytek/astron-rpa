<script setup lang="ts">
import { Auth } from '@rpa/components/auth'

import { useUserStore } from '@/stores/useUserStore'
import { useLinkInvite } from '@/views/Home/components/TeamMarket/hooks/MarketManage/useInviteUser.tsx'

const { marketId } = defineProps({
  marketId: {
    type: String,
    default: '',
  },
})
const emit = defineEmits(['linkChange'])
const userStore = useUserStore()
const { invitData, expireTypes, formState, resetLink } = useLinkInvite(marketId, emit)
</script>

<template>
  <div class="modal-form">
    <a-form
      ref="formRef"
      :model="formState"
      layout="vertical"
      autocomplete="off"
    >
      <a-form-item name="marketName" label="邀请链接">
        <a-input v-model:value="formState.inviteLink" :disabled="invitData.overNumLimit === 1" readonly />
      </a-form-item>
      <a-form-item name="marketName" label="邀请链接">
        <a-select v-model:value="formState.expireType" :disabled="invitData.overNumLimit === 1" :options="expireTypes" />
      </a-form-item>
      <div class="flex items-center w-full text-[12px] text-[#00000090] dark:text-[#FFFFFF99]">
        <span v-if="invitData.overNumLimit === 1 && userStore.currentTenant?.tenantType === 'personal'" class="flex items-center w-full">
          当前市场人数已满十人。开通专业版不限邀请人数，
          <Auth.Consult trigger="button" custom-class="text-primary !w-auto cursor-pointer" :button-conf="{ buttonTxt: '去开通', buttonType: 'text' }" />
          。
        </span>
        <span v-else>邀请有效期至：{{ invitData.expireTime }} <span class="text-primary cursor-pointer hover:opacity-95" @click="resetLink">点击重置</span></span>
      </div>
    </a-form>
  </div>
</template>

<style lang="scss" scoped>
</style>
