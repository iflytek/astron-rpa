<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Table } from 'ant-design-vue'
import type { ColumnsType } from 'ant-design-vue/es/table'
import { useTranslation } from 'i18next-vue'
import { computed, h } from 'vue'

import type { AnyObj } from '@/types/common'

const props = defineProps<{ taskReferInfoList: Array<AnyObj> }>()

const modal = NiceModal.useModal()

const { t } = useTranslation()
const separator = computed(() => t('common.listSeparator'))
const columns = computed<ColumnsType>(() => ([
  {
    title: t('taskRefer.task'),
    dataIndex: 'taskName',
    key: 'taskName',
    width: 150,
    ellipsis: true,
  },
  {
    title: t('taskRefer.robots'),
    key: 'robotNames',
    dataIndex: 'robotNames',
    customRender: ({ record }) => {
      const { robotNames, highIndex } = record
      return h('div', { class: 'robotNames' }, [
        h(
          'span',
          robotNames.map((name, index) => {
            const text = `${index !== 0 ? separator.value : ''}${name}`
            return highIndex.includes(index)
              ? h('span', { style: 'color: #4E68F6; font-weight: bold;' }, text)
              : h('span', text)
          }),
        ),
      ])
    },
  },
]))
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('taskRefer.title')"
    class="referModal"
    :footer="null"
    :width="500"
  >
    <Table
      row-key="taskId"
      :columns="columns"
      :data-source="props.taskReferInfoList"
      :scroll="{ y: 300 }"
      :pagination="false"
      size="small"
    />
  </a-modal>
</template>

<style lang="scss">
.referModal {
  .robotNames {
    display: flex-inline;
    flex-wrap: wrap;
    height: auto;
  }
}
</style>
