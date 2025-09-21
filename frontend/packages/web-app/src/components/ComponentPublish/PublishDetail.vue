<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'
import { Drawer, Spin } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

import { getComponentDetail } from '@/api/project'
import Avatar from '@/components/Avatar/Avatar.vue'

import Group from './Group.vue'
import VersionDetail from './VersionDetail.vue'

const props = defineProps({
  componentId: {
    type: String,
    required: true,
  },
})

const modal = NiceModal.useModal()
const { t } = useTranslation()
const { state, isLoading } = useAsyncState(() => getComponentDetail({ componentId: props.componentId }), null)

const infos = computed(() => ([
  { label: t('componentName'), value: state.value.name },
  { label: t('common.versionNumber'), value: state.value.latestVersion ? `v${state.value.latestVersion}` : '--' },
  { label: t('creator'), value: state.value.creatorName },
]))
</script>

<template>
  <Drawer
    v-bind="NiceModal.antdDrawer(modal)"
    :title="$t('components.componentDetail-1')"
    class="publish-modal"
    :width="568"
    :footer="null"
  >
    <div v-if="isLoading" class="flex items-center justify-center min-h-[60vh]">
      <Spin />
    </div>

    <div v-else class="px-6 flex flex-col gap-4">
      <Group class="py-4" :title="$t('basicInformation')">
        <div class="flex items-center gap-[56px]">
          <Avatar :icon="state.icon" />

          <div class="flex-1 grid grid-cols-3 gap-x-3">
            <div v-for="info in infos" :key="info.label">
              <div class="text-text-secondary text-xs leading-6">
                {{ info.label }}
              </div>
              <div class="pt-2 text-xs">
                {{ info.value }}
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4">
          <div class="text-text-secondary text-xs leading-6">
            {{ $t('components.componentDescription') }}
          </div>

          <div class="mt-2 text-xs whitespace-pre-line">
            {{ state.introduction || '--' }}
          </div>
        </div>
      </Group>

      <Group class="py-4" :title="$t('versionHistory')">
        <template v-for="(item, index) in (state.versionInfoList || [])" :key="item.version">
          <a-divider v-if="index > 0" class="my-3" />
          <VersionDetail :data="item" />
        </template>
      </Group>
    </div>
  </Drawer>
</template>
