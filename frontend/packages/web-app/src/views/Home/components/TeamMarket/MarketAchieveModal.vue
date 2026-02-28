<script setup lang="ts">
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { Input, message, Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { h, reactive, ref } from 'vue'

import { getAppDetails, obtainApp } from '@/api/market'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { ACTUATOR, DESIGNER } from '@/constants/menu'
import { usePermissionStore } from '@/stores/usePermissionStore'
import type { AnyObj } from '@/types/common'
import { SECURITY_RED } from '@/views/Home/components/TeamMarket/config/market.ts'

import type { cardAppItem } from '../../types/market'

interface FormState {
  marketId: string | number
  appId: string | number
  appName: string
  version: string
  obtainDirection: string[]
}

const props = defineProps<{
  record: cardAppItem
  versionLst: AnyObj
}>()

const emit = defineEmits(['refresh', 'limit'])
const permissionStore = usePermissionStore()
const { t } = useTranslation()

const TYPE_ARR = [
  {
    value: 'design',
    permission: DESIGNER,
  },
  {
    value: 'execute',
    permission: ACTUATOR,
  },
] as const

const modal = NiceModal.useModal()
const confirmLoading = ref(false)
const confirmAppName = ref('')

const formRef = ref<FormInstance>()
const formState = reactive<FormState>({
  marketId: props.record.marketId,
  appId: props.record.appId,
  appName: props.record.appName,
  version: props.versionLst[0]?.version,
  obtainDirection: [],
})

async function handleOk() {
  formRef.value.validate().then(() => {
    console.log(formState)
    confirmLoading.value = true
    obtainApp(formState).then((res) => {
      confirmLoading.value = false
      if (res.data?.resultCode === '101') {
        emit('limit')
        modal.hide()
        return
      }
      const commonMsg = t('marketAchieveModal.obtainSuccess')
      formState.obtainDirection.includes('design') && message.success(`${commonMsg}，${t('marketAchieveModal.obtainSuccessDesignSuffix')}`)
      formState.obtainDirection.includes('execute') && message.success(`${commonMsg}，${t('marketAchieveModal.obtainSuccessExecuteSuffix')}`)
      emit('refresh')
      modal.hide()
    }).catch((err) => {
      confirmLoading.value = false
      const { code } = err
      if (![600001, '600001', 600000, '600000'].includes(code)) {
        message.error(err.message || err.msg)
        return
      }
      if ([600001, '600001'].includes(code)) {
        message.error(t('marketAchieveModal.executorVersionExists'))
        return
      }
      if ([600000, '600000'].includes(code)) {
        const modal = GlobalModal.warning({
          title: t('marketAchieveModal.title'),
          content: () => {
            return h('div', [
              h('p', t('marketAchieveModal.duplicateNameTip')),
              h('span', `${t('name')}：`),
              h(Input, {
                defaultValue: formState.appName,
                onChange: (e) => {
                  confirmAppName.value = e.target.value
                  !confirmAppName.value && message.error(t('marketAchieveModal.enterName'))
                },
                style: 'width: 120px',
              }),
            ])
          },
          onOk() {
            if (!confirmAppName.value) {
              message.error(t('marketAchieveModal.enterName'))
              return false
            }
            formState.appName = confirmAppName.value
            handleOk()
            modal.destroy()
          },
          maskClosable: true,
          centered: true,
          keyboard: false,
        })
      }
    })
  })
}

async function checkNumber() {
  if (formState.obtainDirection?.length === 0) {
    return Promise.reject(new Error(t('marketAchieveModal.selectTypeAtLeastOne')))
  }
  return Promise.resolve()
}

// 设置下拉框默认选中版本为当前启用版本
async function setDefaultVersion() {
  getAppDetails({
    marketId: formState.marketId as string,
    appId: formState.appId as string,
  }).then(({ data }) => {
    const enableVersion = data?.versionInfoList.find(item => item.online === 1).versionNum
    formState.version = enableVersion
    console.log('enableVersion', enableVersion)
  })
}

setDefaultVersion()
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="t('marketAchieveModal.obtain')"
    :confirm-loading="confirmLoading"
    centered
    @ok="handleOk"
  >
    <a-form ref="formRef" :model="formState" layout="vertical" autocomplete="off">
      <a-form-item :label="t('marketAchieveModal.obtainVersion')">
        <a-select v-model:value="formState.version">
          <a-select-option v-for="version in props.versionLst" :key="version.version" :value="version.version">
            {{ $t('versionWithNumber', { version: version.version }) }}
          </a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item
        :label="t('marketAchieveModal.obtainTo')"
        name="type"
        :rules="[{ validator: checkNumber, trigger: 'change' }]"
      >
        <a-checkbox-group v-model:value="formState.obtainDirection">
          <a-checkbox v-for="type in TYPE_ARR" :key="type.value" class="leading-[32px]" :value="type.value" :disabled="(props.record.securityLevel === SECURITY_RED && type.value === 'design') || !permissionStore.can(type.permission, 'all')">
            {{ t(`marketAchieveModal.type.${type.value}.label`) }}
            <Tooltip :title="t(`marketAchieveModal.type.${type.value}.tip`)">
              <QuestionCircleOutlined style="color: gray;" />
            </Tooltip>
          </a-checkbox>
        </a-checkbox-group>
        <div v-if="TYPE_ARR.find(item => !permissionStore.can(item.permission, 'all'))" class="text-[12px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)">
          {{ t('marketAchieveModal.notOpenTip', { type: t(`marketAchieveModal.type.${TYPE_ARR.find(item => !permissionStore.can(item.permission, 'all'))?.value}.label`) }) }}
        </div>
      </a-form-item>
    </a-form>
  </a-modal>
</template>
