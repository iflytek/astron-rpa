<script setup lang="ts">
import { Badge, Segmented, Spin } from 'ant-design-vue'

import {
  JOINNUM,
  NOREADNUM,
  READNUM,
  REFUSENUM,
  TEAMMARKETUPDATE,
} from './config'
import { useMessageTip } from './hooks/useMessageTip.ts'

const {
  hasBadage,
  showMessage,
  spinStatus,
  readType,
  tabs,
  handleTabChange,
  messageData,
  messageBoxRef,
  page,
  scroll,
  allRead,
  readMessage,
  joinTeam,
  refuseTeam,
  extractBracketContent,
} = useMessageTip()
</script>

<template>
  <a-dropdown v-model:open="showMessage" placement="bottom">
    <template #overlay>
      <div class="message-tip p-4 rounded-[16px] bg-[#fff] dark:bg-[#141414]">
        <div class="message-tip-head w-full">
          <Segmented v-model:value="readType" :options="tabs" @change="handleTabChange" />
          <a-typography-link class="!text-primary" @click="allRead">
            {{ $t("settingCenter.message.readAllTips") }}
          </a-typography-link>
        </div>
        <div ref="messageBoxRef" class="message-tip-body" @scroll="scroll">
          <div v-for="item in messageData" :key="item.id" class="message-item">
            <div
              class="no-look-icon"
              :class="{ activeIcon: item.operateResult === NOREADNUM }"
            />
            <div class="message-item-desc" @click="readMessage(item)" v-html="extractBracketContent(item.messageInfo)" />
            <div class="message-item-other">
              <span class="create-time text-black/65 dark:text-white/65">{{ item.createTime }}</span>
              <div v-if="item.messageType !== TEAMMARKETUPDATE" class="btnArr mb-[8px]">
                <template v-if="item.operateResult < JOINNUM">
                  <a-button size="small" class="mr-[8px]" @click="refuseTeam(item.id)">
                    {{ $t("settingCenter.message.refuse") }}
                  </a-button>
                  <a-button size="small" type="primary" @click="joinTeam(item.id)">
                    {{ $t("settingCenter.message.join") }}
                  </a-button>
                </template>
                <a-button
                  v-if="item.operateResult === JOINNUM"
                  size="small"
                  :disabled="item.operateResult > READNUM"
                >
                  {{ $t("settingCenter.message.joined") }}
                </a-button>
                <a-button
                  v-if="item.operateResult === REFUSENUM"
                  size="small"
                  class="btn"
                  :disabled="item.operateResult > READNUM"
                >
                  {{ $t("settingCenter.message.refused") }}
                </a-button>
              </div>
              <div v-else class="btnArr">
                <a-button v-if="item.operateResult === READNUM" size="small" class="btn" disabled>
                  {{ $t("settingCenter.message.alreadyRead") }}
                </a-button>
                <a-button v-else size="small" class="btn" @click="readMessage(item)">
                  {{ $t("settingCenter.message.read") }}
                </a-button>
              </div>
            </div>
          </div>
          <div
            v-if="messageData.length === 0 && !spinStatus"
            class="message-item-over h-full flex justify-center items-center"
          >
            <div class="flex flex-col items-center justify-center">
              <rpa-icon name="noresult" class="w-[42px] h-[42px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]" />
              <span class="text-[14px] text-[rgba(0,0,0,0.45)] dark:text-[rgba(255,255,255,0.45)]">{{ $t("settingCenter.message.noMessage") }}</span>
            </div>
          </div>
          <div
            v-else-if="messageData.length >= page.total"
            class="message-item-over"
          >
            {{ $t("settingCenter.message.bottom") }}
          </div>
        </div>
        <Spin :spinning="spinStatus" size="small" class="loading" />
      </div>
    </template>
    <span class="flex items-center justify-center w-full h-full">
      <Badge :dot="hasBadage === '1'" class="message-tip-icon relative">
        <rpa-icon name="notification" />
      </Badge>
    </span>
  </a-dropdown>
</template>

<style lang="scss" scoped>
:deep(.message-tip-icon .ant-badge-dot) {
  position: absolute;
  right: 0;
  top: 0;
}

.message-tip {
  position: relative;
  width: 330px;
  box-shadow:
    0 6px 16px 0 rgba(0, 0, 0, 0.12),
    0 3px 6px -4px rgba(0, 0, 0, 0.12),
    0 9px 28px 8px rgba(0, 0, 0, 0.1);

  .loading {
    position: absolute;
    top: 50%;
    left: 50%;
    margin-top: -5px;
    margin-left: -5px;
  }

  &-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  &-body {
    height: 440px;
    overflow-y: auto;
    box-sizing: border-box;

    &::-webkit-scrollbar {
      display: none;
    }

    .message-item {
      height: 92px;
      margin-bottom: 12px;
      .no-look-icon {
        position: relative;
        height: 20px;
      }
      .activeIcon {
        &::before {
          content: '';
          position: absolute;
          bottom: 2px;
          right: 2px;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #ff3d3d;
        }
      }
      &-desc {
        font-size: $font-size;
        font-weight: 400;
        line-height: 22px;
        cursor: pointer;
      }
      &-other {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        .create-time {
          font-size: $font-size-sm;
        }
        .btnArr {
          display: flex;
          justify-content: space-between;
          align-items: center;
          .btn {
            height: 24px;
            line-height: 24px;
            text-align: center;
            border-radius: 6px;
            margin-right: 10px;
            cursor: pointer;
          }
        }
      }
    }
    .message-item-over {
      padding-top: 10px;
      text-align: center;
    }
  }
}
</style>
