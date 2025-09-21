<script setup lang="ts">
import { LeftOutlined } from '@ant-design/icons-vue'
import { Button, Input, message, Tooltip, Upload } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

const emit = defineEmits(['loginOnLine'])

const { t } = useTranslation()

// const code = ref("");
const mac = ref('')
const fileName = ref('')
const fileTip = ref('')
const flag = ref(false)
const isLoading = ref(false)

function backToOnLine() {
  if (isLoading.value)
    return
  emit('loginOnLine', true)
}

async function codeSubmit() {
  if (!flag.value)
    return message.error(t('configFileInfo'))
  isLoading.value = true
  // await engineLogin({ loginType: "offline", encryptedData: permissionText.value });
  isLoading.value = false
}

function copyText() {
  message.success(t('copySuccess'))
}

async function handleLoad(file: File) {
  const { name } = file
  console.log(name)
}
</script>

<template>
  <div class="LoginBox">
    <div class="LoginBox-offline offline-back" @click="backToOnLine">
      <LeftOutlined /> {{ $t("goBack") }}
    </div>
    <h5 class="LoginBox-offlineTitle">
      {{ $t("offlineLogin") }}
    </h5>
    <div class="title-grey">
      {{ $t("deviceNumber") }}
      <Tooltip :title="$t('deviceNumberTip')">
        <rpa-icon name="question-help" style="font-size: 13px;" class="poniter LoginBox-tipIcon" />
      </Tooltip>
    </div>
    <div class="title-code">
      {{ mac }}
      <Tooltip :title="$t('deviceNumberCopy')">
        <rpa-icon name="list-paste-atom" class="poniter LoginBox-tipIcon" @click="copyText" />
      </Tooltip>
    </div>
    <div class="title-grey">
      {{ $t("configFile") }}
      <Tooltip :title="$t('configFileTip')">
        <rpa-icon name="question-help" style="font-size: 13px;" class="poniter LoginBox-tipIcon" />
      </Tooltip>
    </div>
    <div class="import-content">
      <div class="import-content-input">
        <Input v-model="fileName" allow-clear />
        <div class="import-content-tip" :class="[flag ? 'import-content-tip_success' : 'import-content-tip_error']">
          {{ fileTip }}
        </div>
      </div>
      <Upload
        name="file"
        accept=".license"
        action=""
        :show-upload-list="false"
        :before-upload="(file) => handleLoad(file)"
      >
        <Button type="link">
          {{ $t("clickToUpload") }}
        </Button>
      </Upload>
    </div>
    <div class="code-button">
      <Button type="primary" style="width: 100%" :loading="isLoading" @click="codeSubmit">
        {{ $t("activateNow") }}
      </Button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.LoginBox {
  width: 100%;
  font-size: 14px;
  position: relative;
  text-align: left;

  &-offlineTitle {
    height: 20px;
    font-weight: 600;
    line-height: 22px;
    letter-spacing: 0.2px;
    margin-bottom: 30px;
    font-size: 18px;
  }

  &-offline {
    position: absolute;
    top: -48px;
    font-size: 14px;
    font-weight: 400;
    color: #7b7f9d;
    line-height: 20px;
    letter-spacing: 0.14px;
    user-select: none;
    cursor: pointer;
  }

  &-tipIcon {
    cursor: pointer;
    margin-left: 4px;

    &:hover {
      color: #3c68f6;
    }
  }

  .title-grey {
    height: 20px;
    font-weight: 500;
    color: #999999;
    line-height: 20px;
    letter-spacing: 0.14px;
    margin-bottom: 20px;
  }

  .title-code {
    height: 20px;
    font-weight: 400;
    color: #333333;
    line-height: 20px;
    letter-spacing: 0.14px;
    // margin: 20px 0 34px;
    margin-bottom: 20px;
  }

  .title-code-copy {
    height: 14px;
    font-size: 14px;
    font-weight: 400;
    text-align: center;
    color: #c6c6c6;
    line-height: 14px;
    margin-left: 10px;
  }

  .offline-back {
    left: -13px;
    width: 60px;
  }

  .import-content {
    display: flex;

    &-tip {
      height: 13px;
      font-size: 12px;
      font-weight: 300;
      line-height: 20px;

      &_success {
        color: #29a21c;
      }

      &_error {
        color: #d34d4d;
      }
    }
  }

  .code-button {
    margin-top: 44px;
    margin-bottom: 50px;
  }
}
</style>
