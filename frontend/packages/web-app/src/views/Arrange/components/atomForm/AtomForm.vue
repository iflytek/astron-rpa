<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

import AtomFormItem from './AtomFormItem.vue'
import { useProvideFormStore } from './hooks/useFormStore'

const { i18next } = useTranslation()
const { atomTab, formattedTabs, nodeParameter } = useProvideFormStore()

const activeKey = ref<number>(0)
const sidebarWide = ref(false)
</script>

<template>
  <section class="atom-config h-full relative bg-white dark:bg-[#1d1d1d]" :class="sidebarWide ? 'w-[620px]' : 'w-80'">
    <div v-if="atomTab.length > 0" class="relative atom-config-container h-full overflow-y-auto py-3 px-4">
      <div class="flex items-center mb-4">
        <a-segmented v-model:value="activeKey" block :options="formattedTabs" class="flex-1">
          <template #label="{ title }">
            <span class="text-[12px]">{{ $t(title) }}</span>
          </template>
        </a-segmented>
        <rpa-hint-icon
          :name="sidebarWide ? 'sidebar-wide' : 'sidebar-narrow'"
          :title="sidebarWide ? '切换到窄版' : '切换到宽版'"
          class="ml-[12px]"
          width="16px"
          height="16px"
          enable-hover-bg
          @click="() => sidebarWide = !sidebarWide"
        />
      </div>
      <article
        v-for="item in atomTab[activeKey]?.params" :key="item.key"
        class="tab-container text-[#333] dark:text-[rgba(255,255,255,0.45)]"
      >
        <div v-if="item.name" class="tab-container-label dark:text-[rgba(255,255,255,0.85)] font-bold flex">
          {{ item.name[i18next.language] }}
        </div>
        <template v-for="it in item.formItems" :key="it.key">
          <AtomFormItem v-if="it.show !== false" :atom-form-item="it" @update="nodeParameter?.updateValue" />
        </template>
      </article>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.atom-config {
  .atom-config-container {
    opacity: 1;

    .tab-container {
      font-size: 12px;
      margin-bottom: 24px;

      .tab-container-label {
        font-size: 14px;
        margin-bottom: 12px;
      }
    }

    &::-webkit-scrollbar {
      width: 4px;
    }

    :deep(.ant-tabs-tab) {
      padding: 8px 16px;
    }

    :deep(.ant-tabs-tabpane) {
      padding: 0 10px 10px;
    }
  }

  .atom-config-rectangle {
    width: 20px;
    height: 50px;
    left: -20px;
    line-height: 50px;
    margin-top: -45px;
    font-size: 20px;
    color: #7d7d7d;
    background: #f2f2f2;
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
    z-index: 3;
  }
}
</style>
