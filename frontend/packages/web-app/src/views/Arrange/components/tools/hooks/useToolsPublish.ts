import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import { useRoute } from 'vue-router'

import i18next from '@/plugins/i18next'

import { ComponentPublishModal } from '@/components/ComponentPublish'
import { PublishModal } from '@/components/PublishComponents'
import { useProcessStore } from '@/stores/useProcessStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsPublish() {
  const processStore = useProcessStore()
  const projectId = useRoute()?.query?.projectId as string

  const publish = () => {
    if (processStore.isComponent) {
      NiceModal.show(ComponentPublishModal, { componentId: projectId })
    }
    else {
      NiceModal.show(PublishModal, { robotId: projectId })
    }
  }

  const item: ArrangeTools = {
    key: 'publish',
    title: 'release',
    name: 'release',
    fontSize: '',
    icon: 'tools-publish',
    action: '',
    loading: false,
    show: true,
    disable: ({ status }) => ['debug', 'run'].includes(status),
    clickFn: () => {
      processStore.saveProject()
      publish()
    },
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning(i18next.t('arrange.tryLaterWhileRunningOrDebug'))
      }

      return !disable
    },
  }

  return item
}
