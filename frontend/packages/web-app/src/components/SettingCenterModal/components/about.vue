<script setup lang="ts">
import { message } from "ant-design-vue";
import { useTranslation } from "i18next-vue";
import { storeToRefs } from "pinia";
import { computed } from "vue";

import { useAppConfigStore } from "@/stores/useAppConfig";

import Card from "../components/card.vue";

const { t } = useTranslation();
const appStore = useAppConfigStore();
const { appInfo, updaterState } = storeToRefs(appStore);

const textItems = computed(() => [
  {
    key: t("settingCenter.about.installDirectory"),
    id: "installDirectory",
    content: appInfo.value.appPath,
    copyable: {
      onCopy: () => {
        message.success(t('copySuccess'))
      }
    },
  },
  {
    key: t("settingCenter.about.userDirectory"),
    id: "userDirectory",
    content: appInfo.value.userPath,
    copyable: {
      onCopy: () => {
        message.success(t('copySuccess'))
      }
    },
  },
  {
    key: t("settingCenter.about.buildVersion"),
    id: "buildVersion",
    content: appInfo.value.buildInfo,
  },
  {
    key: t("settingCenter.about.systemEnvironment"),
    id: "systemEnvironment",
    content: appInfo.value.systemInfo,
  },
]);

async function checkUpdate() {
  await appStore.checkUpdate(true);
}
</script>

<template>
  <div class="w-full h-full relative">
    <Card
      class="h-[84px] px-[24px] py-[20px] !gap-4"
      :title="$t('app')"
      :description="`v${appInfo.appVersion}`"
    >
      <template #prefix>
        <img src="/icons/icon.png" width="40" height="40" />
      </template>
      <template #suffix>
        <a-button :loading="updaterState.checkLoading" @click="checkUpdate">
          {{ t("settingCenter.about.checkUpdate") }}
        </a-button>
      </template>
    </Card>
    <div class="w-full p-[24px]">
      <div
        class="grid gap-x-2 gap-y-3 text-sm"
        style="grid-template-columns: max-content 1fr"
      >
        <template v-for="item in textItems" :key="item.key">
          <div class="text-right">{{ item.key }}:</div>
          <a-typography-paragraph
            class="!mb-0 min-w-0"
            :ellipsis="{ rows: 1, tooltip: true }"
            :content="item.content"
            :copyable="item.copyable"
          />
        </template>
      </div>
    </div>
    <div
      class="absolute w-full bottom-0 text-center text-text-tertiary text-xs"
    >
      生成式人工智能服务能力由 星火认知大模型 -
      Anhui-XingHuoRenZhiDaMoXing-20230823 提供
    </div>
  </div>
</template>
