<script lang="ts" setup>
import { SearchOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { useTranslation } from 'i18next-vue'
import { debounce } from 'lodash-es'
import { ref } from 'vue'

import { getRobotList } from '@/api/task'

const emit = defineEmits(['ok'])

const modal = NiceModal.useModal()
const { t } = useTranslation()

const searchText = ref('')
const intenalRobotList = ref([])

function handleSearch() {
  getRobots()
}

const handleChange = debounce(() => getRobots(), 600, { trailing: true })

function okhandle() {
  const checkedList = intenalRobotList.value.filter(item => item.checked)
  emit('ok', checkedList)
  modal.hide()
}

function getRobots() {
  getRobotList({ name: searchText.value }).then((res) => {
    intenalRobotList.value = res.data.map(i => ({
      ...i,
      checked: false,
    })) ?? []
  })
}

getRobots()
</script>

<template>
  <a-modal v-bind="NiceModal.antdModal(modal)" :title="t('selectRobots')" width="400px" @ok="okhandle">
    <a-input v-model:value="searchText" :placeholder="t('searchRobots')" @change="handleChange" @search="handleSearch">
      <template #prefix>
        <SearchOutlined />
      </template>
    </a-input>
    <div class="search-result">
      <div v-for="item in intenalRobotList" :key="item.id" class="mb-2">
        <a-checkbox :key="item.robotId" v-model:checked="item.checked" :value="item.robotId" class="robot-item">
          {{ item.robotName }}
        </a-checkbox>
      </div>
      <a-empty v-if="intenalRobotList.length === 0" />
    </div>
  </a-modal>
</template>

<style scoped>
.search-result {
  margin-top: 10px;
  max-height: 400px;
  height: 200px;
  overflow-y: auto;
}
</style>
