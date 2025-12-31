<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { checkProjectNum, createProject, getDefaultName } from '@/api/project'
import { ARRANGE } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { newProjectModal } from '@/views/Home/components/modals'

import Banner from '../components/Banner.vue'
import TableContainer from '../components/TableContainer.vue'
import { Auth } from '@rpa/components/auth'
import { useUserStore } from '@/stores/useUserStore'

const { t } = useTranslation()
const userStore = useUserStore()
const consultRef = ref<InstanceType<typeof Auth.Consult> | null>(null)

async function createRobot() {
  if(userStore.currentTenant?.tenantType !== 'enterprise'){
    const res = await checkProjectNum()
    if(!res.data){
      consultRef.value?.init({
        trigger: 'modal',
        modalConfirm: {
          title: '已达到应用数量上限',
          content: userStore.currentTenant?.tenantType === 'personal' ? `个人版最多支持创建19个应用，您已满额。` : `专业版最多支持创建99个应用，您已满额。`,
          okText: userStore.currentTenant?.tenantType === 'personal' ? '升级至专业版' : '升级至企业版',
          cancelText: '我知道了',
        },
        consult: {
          consultTitle: userStore.currentTenant?.tenantType === 'personal' ? '专业版咨询' : '企业版咨询',
          consultEdition: userStore.currentTenant?.tenantType === 'personal' ? 'professional' : 'enterprise',
          consultType: 'consult',
        }
      })
      return
    }
  }
  const loading = ref(false)
  newProjectModal.show({
    title: t('newProject'),
    name: t('projectName'),
    loading,
    defaultName: getDefaultName,
    onConfirm: (name: string) => newProject(name),
  })

  const newProject = async (projectName: string) => {
    try {
      loading.value = true
      const res = await createProject({ name: projectName })
      const projectId = res.data.robotId

      useRoutePush({ name: ARRANGE, query: { projectId, projectName } })
      message.success('新建成功')
    }
    finally {
      newProjectModal.hide()
      loading.value = false
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
    <Auth.Consult ref="consultRef" :trigger="'modal'"/>
  </div>
</template>
