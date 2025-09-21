<script lang="ts" setup>
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

const handleChange = debounce(() => {
  getRobots()
}, 600, { trailing: true })

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
    <!-- 上面是个搜索框， 下面是个列表，每一项有名称和前面的checkbox -->
    <div class="robot-select">
      <a-input-search v-model:value="searchText" :placeholder="t('searchRobots')" @change="handleChange" @search="handleSearch" />
      <div class="search-result">
        <div v-for="item in intenalRobotList" :key="item.id" class="mb-2">
          <a-checkbox :key="item.robotId" v-model:checked="item.checked" :value="item.robotId" class="robot-item">
            {{ item.robotName }}
          </a-checkbox>
        </div>
        <a-empty v-if="intenalRobotList.length === 0" />
      </div>
    </div>
  </a-modal>
</template>

<style scoped>
.robot-select {
  max-height: 500px;
}

.search-result {
  padding-top: 10px;
  max-height: 400px;
  height: 200px;
  overflow-y: auto;
}

.ant-checkbox-group {
  flex-direction: column;
}
:deep(.ant-input) {
  height: 32px;
}
:deep(.ant-input-search-button) {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
