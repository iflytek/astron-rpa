<script lang="ts" setup>
import { PlusCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Popconfirm } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { h, reactive, ref } from 'vue'

import { apiDeleteMail, apiGetMailList } from '@/api/mail'

import { MailModal } from './index'

defineProps({
  data: {
    type: Array,
  },
})

const createMailModal = NiceModal.useModal(MailModal)

const { t } = useTranslation()
const modal = NiceModal.useModal()

const columns = [
  {
    title: t('mailTitle'),
    dataIndex: 'emailAccount',
    key: 'emailAccount',
  },
  {
    title: t('operate'),
    key: 'action',
    dataIndex: 'action',
    width: 120,
  },
]

const pagination = reactive({
  pageSize: 5,
  total: 0,
  showTotal: total => t('totalItems', { total }),
  current: 1,
  onChange: (page) => {
    pagination.current = page
    getMailList()
  },
})

const data = ref([])

function getMailList() {
  apiGetMailList({
    pageNo: pagination.current,
    pageSize: pagination.pageSize,
  }).then((res) => {
    const { records, total, current } = res.data
    pagination.total = total
    pagination.current = current
    data.value = records
  })
}

function addMail() {
  createMailModal.show({
    data: {},
    onOk: () => getMailList(),
  })
}

function editMail(item: object) {
  createMailModal.show({
    data: item,
    onOk: () => getMailList(),
  })
}

async function deleteMail(resourceId: string) {
  await apiDeleteMail({ resourceId })
  await getMailList()
}

getMailList()
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="mail-list-modal"
    :title="t('mailManage')"
    :footer="null"
    :width="500"
  >
    <a-table
      class="mail-list-table"
      size="small"
      height=""
      :columns="columns"
      :data-source="data"
      row-key="id"
      :pagination="pagination"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'action'">
          <a-button
            class="action-btn"
            type="link"
            @click="() => editMail(record)"
          >
            {{ t("edit") }}
          </a-button>
          <Popconfirm
            :title="t('deleteConfirmTip')"
            @confirm="() => deleteMail(record.resourceId)"
          >
            <a-button class="action-btn" type="link">
              {{ t("delete") }}
            </a-button>
          </Popconfirm>
        </template>
      </template>
    </a-table>
    <!-- 新增 -->
    <a-button
      class="flex justify-center align-center mt-4"
      type="primary"
      block
      :icon="h(PlusCircleOutlined)"
      @click="addMail"
    >
      {{ t("mailManageConfig.addEmail") }}
    </a-button>
  </a-modal>
</template>

<style lang="scss" scoped>
.action-btn {
  padding: 0 4px;
  color: var(--color-primary);
}
.ant-btn > span {
  display: inline-flex;
}

.mail-list-table {
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-secondary);

  :deep(.ant-table-thead > tr > th) {
    background: #f3f3f7;
  }
}
.dark .mail-list-table {
  :deep(.ant-table-thead > tr > th) {
    background: #2f2f2f;
  }
}
</style>
