<script lang="ts" setup>
import { MailOutlined } from '@ant-design/icons-vue'
import { useTranslation } from 'i18next-vue'
import { NiceModal } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'

import { apiGetMailList } from '@/api/mail'

import { MailListModal } from './MailModal'

interface MailItem {
  label: string,
  value: string,
  data: RPA.IMailItem
}

const props = defineProps<{ placeholder?: string }>()

const modalValue = defineModel<string | undefined>('value', { default: undefined })

const emit = defineEmits<{
  (e: 'change', value: RPA.IMailItem): void
}>()

const { t } = useTranslation()

const { state: mailList, execute } = useAsyncState<MailItem[]>(async () => {
  const { records } = await apiGetMailList({ pageNo: 1, pageSize: 100 })
  return records.map((item) => ({
    value: item.emailAccount,
    label: item.emailAccount,
    data: item,
  }))
}, [])

function handleChange(value: string) {
  modalValue.value = value
  const mailItem = mailList.value.find(item => item.value === value)
  mailItem && emit('change', mailItem.data)
}

function mailModal() {
  NiceModal.show(MailListModal, {
    onClose: execute,
  })
}

</script>

<template>
  <a-select
    :value="modalValue || undefined"
    style="width: 100%"
    :placeholder="props.placeholder"
    :options="mailList"
    @change="handleChange"
  >
    <template #suffixIcon>
      <a-tooltip :title="t('mailManage')">
        <MailOutlined class="cursor-pointer text-base hover:text-primary" @click="mailModal" />
      </a-tooltip>
    </template>
  </a-select>
</template>
