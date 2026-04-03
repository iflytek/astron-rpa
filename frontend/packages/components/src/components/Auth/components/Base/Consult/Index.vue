<script setup lang="ts">
import { Button, Modal } from "ant-design-vue";
import { ref } from "vue";

import { Icon as RpaIcon } from "../../../../Icon";
import type { AuthType } from "../../../interface";

import ConsultModal from "./ConsultModal.vue";

type TriggerType = "button" | "modal";

interface ButtonConf {
  buttonType: "tag" | "text" | "button";
  buttonTxt?: string;
  currentEdition?: "personal" | "professional" | "enterprise";
  expirationDate?: string;
  shouldAlert?: boolean;
}

interface ModalConfirmConf {
  title: string;
  content: string;
  okText: string;
  cancelText: string;
}

interface ConsultConf {
  consultTitle?: string;
  consultEdition?: "professional" | "enterprise";
  consultType: "consult" | "renewal";
}

interface Props {
  authType?: AuthType;
  trigger?: TriggerType;
  buttonConf?: ButtonConf;
  customClass?: string;
  modalConfirm?: ModalConfirmConf;
  consult?: ConsultConf;
}

const props = withDefaults(defineProps<Props>(), {
  authType: "uap",
  trigger: "button",
});

const tenantTypeMap = {
  personal: "components.auth.personalFree",
  professional: "components.auth.professional",
  enterprise: "components.auth.enterprise",
};

const confData = ref(props);
const consultModalRef = ref<InstanceType<typeof ConsultModal> | null>(null);
function openModal() {
  if (confData.value.authType !== "casdoor") consultModalRef.value?.showModal();
}

function init(config: typeof props) {
  confData.value = config;
  if (confData.value.trigger === "modal") {
    Modal.confirm({
      ...confData.value.modalConfirm!,
      onOk: () => openModal(),
    });
  }
}

defineExpose({
  init,
});
</script>

<template>
  <div class="w-full" :class="confData?.customClass">
    <template v-if="confData?.trigger === 'button'">
      <div
        v-if="confData?.buttonConf?.buttonType === 'tag'"
        class="cursor-pointer flex items-center justify-start text-gradient-bg text-upgrader-bg !rounded-[12px] !w-full !text-[14px] hover:!opacity-90"
      >
        <div
          v-if="
            confData?.buttonConf?.currentEdition &&
            confData?.buttonConf?.currentEdition !== 'personal'
          "
        >
          <div class="w-[fit-content] font-bold">
            <span class="text-gradient">
              {{ $t(tenantTypeMap[confData?.buttonConf?.currentEdition]) }}
            </span>
          </div>
          <span
            v-if="confData?.buttonConf?.expirationDate"
            class="text-[12px] mt-[8px]"
          >
            {{ $t("components.auth.expirationDateLabel") }}
            {{ confData?.buttonConf?.expirationDate }}
            <span
              v-if="confData?.buttonConf?.shouldAlert"
              class="bg-[#ec483e] text-white px-[6px] py-[1px] !text-[12px] rounded-[3px]"
            >
              {{ $t("components.auth.expiringSoon") }}
            </span>
          </span>
        </div>
        <div
          v-else
          class="w-full text-left"
          :class="{
            'min-h-[38px] leading-[38px]':
              !confData?.buttonConf?.currentEdition,
          }"
          @click="openModal"
        >
          <div
            v-if="confData?.buttonConf?.currentEdition"
            class="w-[fit-content] font-bold"
          >
            <span class="text-gradient">
              {{ $t(tenantTypeMap[confData?.buttonConf?.currentEdition]) }}
            </span>
          </div>
          <div
            v-if="confData?.authType !== 'casdoor'"
            class="flex items-center justify-start"
            :class="{
              'text-[12px] mt-[2px]': confData?.buttonConf?.currentEdition,
            }"
          >
            <RpaIcon
              class="w-[26px] h-[26px] mr-[8px]"
              :class="{
                '!w-[20px] !h-[20px] !mr-[4px]':
                  confData?.buttonConf?.currentEdition,
              }"
              name="upgrade-icon"
            />
            <span class="text-gradient">
              {{
                confData?.buttonConf?.buttonTxt ||
                $t("components.auth.upgradeProEnterprise")
              }}
            </span>
          </div>
        </div>
      </div>
      <span
        v-else-if="confData?.buttonConf?.buttonType === 'text'"
        @click="openModal"
      >
        {{ confData?.buttonConf?.buttonTxt }}
      </span>
      <Button
        v-else
        type="primary"
        ghost
        block
        class="border !border-[#0000001A] dark:!border-[#FFFFFF29]"
        @click="openModal"
      >
        <span
          class="!flex items-center justify-center text-[12px] text-[#000000D9] dark:text-[#FFFFFFD9]"
        >
          <RpaIcon
            class="w-[16px] h-[16px] mr-[4px]"
            name="python-package-plus"
          />
          <span>
            {{
              confData?.buttonConf?.buttonTxt ||
              $t("components.auth.createWorkspace")
            }}
          </span>
        </span>
      </Button>
    </template>
    <ConsultModal ref="consultModalRef" v-bind="confData?.consult" />
  </div>
</template>
