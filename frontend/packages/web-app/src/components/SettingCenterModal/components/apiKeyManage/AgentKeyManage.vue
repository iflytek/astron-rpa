<script setup lang="ts">
import { DeleteOutlined, EditOutlined, EyeInvisibleOutlined, EyeOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { message, Space } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, h, reactive, ref } from 'vue'

import { deleteAgentAPI, getAgentApis } from '@/api/setting'
import GlobalModal from '@/components/GlobalModal/index.ts'
import NormalTable from '@/components/NormalTable/index.vue'
import type { TableColumnConfig, TableOption } from '@/types/normalTable'

import { StarAgentModal } from './modals'
import type { AgentData } from './starAgentModal.vue'

const { t } = useTranslation()
const currStarTableRef = ref(null)
const secretVisibleId = ref([])

function refreshHomeTable() {
  currStarTableRef.value?.fetchTableData()
}

function toggleSecretVisible(id: string) {
  if (secretVisibleId.value.includes(id)) {
    secretVisibleId.value = secretVisibleId.value.filter(item => item !== id)
  }
  else {
    secretVisibleId.value.push(id)
  }
}

const columns = computed<TableColumnConfig[]>(() => [
  {
    title: t('name'),
    dataIndex: 'name',
    key: 'name',
    align: 'left',
    width: 80,
    ellipsis: true,
  },
  {
    title: 'APP ID',
    dataIndex: 'app_id',
    key: 'app_id',
    width: 140,
    ellipsis: true,
  },
  {
    title: 'API Key',
    dataIndex: 'api_key',
    key: 'api_key',
    width: 140,
    ellipsis: true,
  },
  {
    title: 'API Secret',
    dataIndex: 'api_secret',
    key: 'api_secret',
    ellipsis: true,
    customRender: ({ record }) => {
      const isVisible = secretVisibleId.value.includes(record.id)

      return h('div', { class: 'flex items-center group' }, [
        h('span', { class: 'truncate w-full' }, isVisible ? record.api_secret : '********'),
        h(isVisible ? EyeInvisibleOutlined : EyeOutlined, {
          class: 'cursor-pointer invisible group-hover:visible',
          onClick: () => toggleSecretVisible(record.id),
        }),
      ])
    },
  },
  {
    title: t('operate'),
    dataIndex: 'oper',
    key: 'oper',
    align: 'center',
    width: 100,
    customRender: ({ record }) => h(Space, [
      h(EditOutlined, { onClick: () => editAgentKey(record) }),
      h(DeleteOutlined, { onClick: () => deleteApiKey(record) }),
    ]),
  },
])

const starTableOption = reactive<TableOption>({
  refresh: true,
  getData: getAgentApis,
  buttonListAlign: 'right',
  headerClass: '!justify-end',
  buttonList: [{
    label: '新建',
    clickFn: addAgentKey,
    type: 'primary',
    hidden: false,
  }],
  tableProps: {
    columns,
    rowKey: 'id',
    scroll: { y: 180 },
    size: 'small',
  },
  params: {},
})

function addAgentKey() {
  NiceModal.show(StarAgentModal, {
    onRefresh: () => refreshHomeTable(),
  })
}

function deleteApiKey(row: AgentData) {
  GlobalModal.confirm({
    title: t('settingCenter.apiKeyManage.deleteApiKeyConfirm'),
    onOk: async () => {
      await deleteAgentAPI(row.id)
      message.success(t('deleteSuccess'))
      refreshHomeTable()
    },
    centered: true,
    keyboard: false,
  })
}

function editAgentKey(row: AgentData) {
  NiceModal.show(StarAgentModal, {
    data: row,
    onRefresh: () => refreshHomeTable(),
  })
}
</script>

<template>
  <NormalTable ref="currStarTableRef" :option="starTableOption" />
</template>
