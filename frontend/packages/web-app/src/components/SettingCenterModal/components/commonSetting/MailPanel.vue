<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import { MailListModal } from '@/components/MailManage/MailModal'

import Card from '../card.vue'

function handleManageClick() {
  NiceModal.show(MailListModal)
}

</script>

<template>
  <Card class="px-5 py-4" :title="$t('mailManage')" :description="$t('settingCenter.mailManage.subtitle')">
    <template #suffix>
      <a-button type="primary" size="small" @click="handleManageClick">
        {{ $t('settingCenter.mailManage.manage') }}
      </a-button>
    </template>
  </Card>
</template>
