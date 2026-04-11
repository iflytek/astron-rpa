<script setup lang="ts">
import { ExclamationCircleFilled } from '@ant-design/icons-vue'
import { Button, Modal } from 'ant-design-vue'
import { onBeforeUnmount, reactive, ref } from 'vue'

import { getMacPermissionStatus, openMacPermissionSettings, type MacPermissions } from '@/api/macPermission'
import BUS from '@/utils/eventBus'

const visible = ref(false)
const hasChanged = ref(false)
const allGranted = ref(false)
const ignored = ref(false)

const permissions = reactive<MacPermissions>({
  accessibility: false,
  screen_recording: false,
  full_disk_access: false,
})

let initialSnapshot: MacPermissions | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null

const permissionConfig: Array<{
  key: keyof MacPermissions
  label: string
  desc: string
}> = [
  {
    key: 'accessibility',
    label: '辅助功能',
    desc: '用于模拟鼠标点击、键盘输入等自动化操作',
  },
  {
    key: 'screen_recording',
    label: '屏幕录制',
    desc: '用于截图识别、视觉定位等屏幕内容分析',
  },
  {
    key: 'full_disk_access',
    label: '完全磁盘访问',
    desc: '用于读写文件、访问受保护目录等操作',
  },
]

function open(perms: MacPermissions) {
  Object.assign(permissions, perms)
  initialSnapshot = { ...perms }
  hasChanged.value = false
  allGranted.value = Object.values(perms).every(Boolean)
  ignored.value = false
  visible.value = true
}

function handleIgnore() {
  ignored.value = true
  visible.value = false
  stopPolling()
}

function handleClose() {
  visible.value = false
  stopPolling()
}

async function handleOpenSettings(type: keyof MacPermissions) {
  await openMacPermissionSettings(type)
  startPolling()
}

function startPolling() {
  if (pollTimer)
    return
  pollTimer = setInterval(async () => {
    try {
      const res = await getMacPermissionStatus()
      const latest: MacPermissions = res.data.data
      Object.assign(permissions, latest)

      const changed = (Object.keys(latest) as Array<keyof MacPermissions>).some(
        k => initialSnapshot && !initialSnapshot[k] && latest[k],
      )
      if (changed)
        hasChanged.value = true

      if (Object.values(latest).every(Boolean)) {
        allGranted.value = true
        stopPolling()
      }
    }
    catch {}
  }, 1000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function handleBusEvent(perms: MacPermissions) {
  open(perms)
}

BUS.$off('mac-permission-check', handleBusEvent)
BUS.$on('mac-permission-check', handleBusEvent)

onBeforeUnmount(() => {
  BUS.$off('mac-permission-check', handleBusEvent)
  stopPolling()
})
</script>

<template>
  <Modal
    :open="visible"
    :closable="false"
    :mask-closable="false"
    :footer="null"
    :z-index="99999"
    :width="520"
    centered
  >
    <!-- 标题区 -->
    <div class="perm-header">
      <ExclamationCircleFilled class="perm-header__icon" />
      <div>
        <div class="perm-header__title">需要系统权限</div>
        <div class="perm-header__sub">以下权限缺失将影响自动化功能的正常运行，建议前往系统设置完成授权</div>
      </div>
    </div>

    <!-- 权限列表 -->
    <div class="perm-list">
      <div
        v-for="item in permissionConfig"
        :key="item.key"
        class="perm-item"
        :class="{ 'perm-item--granted': permissions[item.key] }"
      >
        <div class="perm-item__status">
          <span v-if="permissions[item.key]" class="perm-dot perm-dot--ok" />
          <span v-else class="perm-dot perm-dot--err" />
        </div>
        <div class="perm-item__info">
          <div class="perm-item__name">{{ item.label }}</div>
          <div class="perm-item__desc">{{ item.desc }}</div>
        </div>
        <div class="perm-item__action">
          <span v-if="permissions[item.key]" class="perm-tag perm-tag--ok">已授权</span>
          <Button
            v-else
            size="small"
            type="primary"
            @click="handleOpenSettings(item.key)"
          >
            前往设置
          </Button>
        </div>
      </div>
    </div>

    <!-- 变更提示 -->
    <div v-if="hasChanged" class="perm-notice">
      <ExclamationCircleFilled style="color: #faad14; margin-right: 6px;" />
      权限已更新，重启应用后生效
    </div>

    <!-- 底部操作 -->
    <div class="perm-footer">
      <Button @click="handleIgnore">
        暂时忽略
      </Button>
      <Button
        v-if="allGranted || hasChanged"
        type="primary"
        @click="handleClose"
      >
        已完成授权，重启应用
      </Button>
    </div>
  </Modal>
</template>

<style scoped>
.perm-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding-bottom: 20px;
  margin-bottom: 4px;
}

.perm-header__icon {
  font-size: 24px;
  color: var(--color-warning, #faad14);
  margin-top: 2px;
  flex-shrink: 0;
}

.perm-header__title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text, rgba(0,0,0,0.85));
  line-height: 1.4;
  margin-bottom: 4px;
}

.perm-header__sub {
  font-size: 13px;
  color: var(--color-text-secondary, rgba(0,0,0,0.45));
  line-height: 1.6;
}

.perm-list {
  padding: 8px 0;
}

.perm-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 12px;
  border-radius: 8px;
  margin-bottom: 6px;
  background: var(--color-bg-layout, #fafafa);
  transition: background 0.2s;
}

.perm-item--granted {
  background: rgba(82, 196, 26, 0.06);
}

.perm-item__status {
  flex-shrink: 0;
}

.perm-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.perm-dot--ok {
  background: var(--color-success, #52c41a);
  box-shadow: 0 0 0 3px rgba(82, 196, 26, 0.15);
}

.perm-dot--err {
  background: var(--color-error, #ff4d4f);
  box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.15);
}

.perm-item__info {
  flex: 1;
  min-width: 0;
}

.perm-item__name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text, rgba(0,0,0,0.85));
  margin-bottom: 2px;
}

.perm-item__desc {
  font-size: 12px;
  color: var(--color-text-secondary, rgba(0,0,0,0.45));
  line-height: 1.5;
}

.perm-item__action {
  flex-shrink: 0;
}

.perm-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.perm-tag--ok {
  color: var(--color-success, #52c41a);
  background: rgba(82, 196, 26, 0.1);
}

.perm-notice {
  display: flex;
  align-items: center;
  margin-top: 12px;
  padding: 10px 14px;
  background: rgba(250, 173, 20, 0.08);
  border: 1px solid rgba(250, 173, 20, 0.3);
  border-radius: 6px;
  font-size: 13px;
  color: var(--color-text, rgba(0,0,0,0.85));
}

.perm-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 20px;
  padding-top: 16px;
}
</style>