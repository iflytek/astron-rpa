<script setup lang="ts">
import { useTranslation } from 'i18next-vue'

import type { InviteInfo } from '../../interface'

const { inviteInfo } = defineProps<{
  inviteInfo: InviteInfo
}>()

const { t } = useTranslation()
</script>

<template>
  <div class="text-[20px] md:text-[14px] mb-[24px] text-center text-[#000000D9] dark:text-[#FFFFFF]">
    <div>{{ inviteInfo.inviterName }} <span class="text ml-[5px]">{{ t('components.auth.inviteJoin') }}{{ inviteInfo.inviteType === 'market' ? t('components.auth.market') : t('components.auth.workspace') }}</span></div>
    <div class="text-[32px] md:text-[20px] mt-[10px] font-[600]">
      {{ inviteInfo.inviteType === 'market' ? inviteInfo.marketName : inviteInfo.deptName }}
    </div>
  </div>
</template>
