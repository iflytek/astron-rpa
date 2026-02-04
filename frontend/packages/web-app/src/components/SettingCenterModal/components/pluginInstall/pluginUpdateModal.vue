<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('pluginUpdateTip')"
    width="500px"
    @cancel="handleClose"
    centered
  >
    <div class="update-modal-content">
      <div class="icon-wrapper">
        <ExclamationCircleFilled class="warning-icon" />
      </div>
      <div class="text-content">
        <p>{{ $t("pluginUpdateInfo") }}</p>
        <p>{{ $t("pluginUpdateDesc") }}</p>
        <p class="warning-text">
          {{ $t("pluginUpdateNotice") }}
        </p>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <a-button @click="handleClose">{{ $t("updateLater") }}</a-button>
        <a-button type="primary" @click="handleConfirm">
         {{ $t("updateNow")}}
        </a-button>
      </div>
    </template>
  </a-modal>
</template>

<script setup>
import { NiceModal } from '@rpa/components'
import { Modal as AModal, Button as AButton } from 'ant-design-vue';
import { ExclamationCircleFilled } from '@ant-design/icons-vue';

const modal = NiceModal.useModal()

const handleClose = () => {
  modal.hide();
};

const handleConfirm = () => {
  modal.resolve('confirm')
  handleClose();
};
</script>

<style scoped>
.update-modal-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 12px 0;
}

.icon-wrapper {
  flex-shrink: 0;
  margin-top: 4px;
}

.warning-icon {
  font-size: 22px;
  color: #faad14;
}

.text-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  line-height: 1.6;
}

.text-content p {
  margin: 0;
}

.warning-text {
  color: #8c8c8c;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  gap: 8px;
}
</style>