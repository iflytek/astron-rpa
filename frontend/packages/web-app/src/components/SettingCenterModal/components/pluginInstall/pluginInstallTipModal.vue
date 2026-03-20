<script setup>
import { ExclamationCircleFilled } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Button as AButton, Modal as AModal } from 'ant-design-vue'

const modal = NiceModal.useModal()

function handleClose() {
  modal.hide()
}

function handleConfirm() {
  modal.resolve('confirm')
  handleClose()
}
</script>

<template>
  <AModal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('pluginInstallTip')"
    width="500px"
    centered
    :mask-closable="false"
    @cancel="handleClose"
  >
    <div class="update-modal-content">
      <div class="icon-wrapper">
        <ExclamationCircleFilled class="warning-icon" />
      </div>
      <div class="text-content">
        <p>{{ $t("pluginInstallInfo") }}</p>
        <p>{{ $t("pluginInstallDesc") }}</p>
        <p class="warning-text">
          {{ $t("pluginInstallNotice") }}
        </p>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <AButton @click="handleClose">
          {{ $t("installLater") }}
        </AButton>
        <AButton type="primary" @click="handleConfirm">
          {{ $t("installNow") }}
        </AButton>
      </div>
    </template>
  </AModal>
</template>

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
