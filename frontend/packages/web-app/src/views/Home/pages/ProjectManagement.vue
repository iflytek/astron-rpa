<script setup lang="ts">
import { Auth } from '@rpa/components/auth'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

import { checkProjectNum, createProject, getDefaultName } from '@/api/project'
import { ARRANGE } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useUserStore } from '@/stores/useUserStore'
import { newProjectModal } from '@/views/Home/components/modals'

import Banner from '../components/Banner.vue'
import TableContainer from '../components/TableContainer.vue'

const { t } = useTranslation()
const appStore = useAppConfigStore()
const userStore = useUserStore()
const { appInfo } = storeToRefs(appStore)
const consultRef = ref<InstanceType<typeof Auth.Consult> | null>(null)

async function createRobot() {
  if (userStore.currentTenant?.tenantType !== 'enterprise') {
    const res = await checkProjectNum()
    if (!res.data) {
      consultRef.value?.init({
        authType: appInfo.value.appAuthType,
        trigger: 'modal',
        modalConfirm: {
          title: t('designerManage.limitReachedTitle'),
          content: userStore.currentTenant?.tenantType === 'personal'
            ? t('designerManage.personalLimitReachedContent')
            : t('designerManage.proLimitReachedContent'),
          okText: userStore.currentTenant?.tenantType === 'personal'
            ? t('designerManage.upgradeToPro')
            : t('designerManage.upgradeToEnterprise'),
          cancelText: t('designerManage.gotIt'),
        },
        consult: {
          consultTitle: t('designerManage.consult'),
          consultEdition: userStore.currentTenant?.tenantType === 'personal' ? 'professional' : 'enterprise',
          consultType: 'consult',
        },
      })
      return
    }
  }

  newProjectModal.show({
    title: t('newProject'),
    name: t('projectName'),
    defaultName: getDefaultName,
    onConfirm: (name: string) => newProject(name),
  })

  const newProject = async (projectName: string) => {
    try {
      const res = await createProject({ name: projectName })
      const projectId = res.data.robotId

      useRoutePush({ name: ARRANGE, query: { projectId, projectName } })
      message.success(t('createSuccess'))
    }
    finally {
      newProjectModal.hide()
    }
  }
}
</script>

<template>
  <div class="h-full flex flex-col z-10 relative">
    <Banner
      :title="$t('designerManage.oneClickAutomation')"
      :sub-title="$t('designerManage.freeFromRepetition')"
      :action-text="$t('designerManage.createRobot')"
      @action="createRobot"
    />
    <TableContainer>
      <router-view />
    </TableContainer>
    <Auth.Consult ref="consultRef" trigger="modal" :auth-type="appInfo.appAuthType" />
  </div>
</template>
