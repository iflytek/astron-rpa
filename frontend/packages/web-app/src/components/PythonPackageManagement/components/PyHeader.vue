<script setup lang="ts">
import { pythonInstallModal } from '../modals'

const sidebarWide = defineModel('sidebarWide')
</script>

<template>
  <div class="pythonDependence_header flex items-center">
    <span
      class="python-header-title flex-1 text-[rgba(0, 0, 0, 0.85)] dark:text-[rgba(255,255,255,0.85)]"
    >
      Python包管理
    </span>
    <div class="pythonDependence-right">
      <rpa-hint-icon
        name="python-package-plus"
        class="pythonDependence-plus"
        enable-hover-bg
        @click="pythonInstallModal.show()"
      >
        <template #suffix>
          {{ $t("newPythonPackage") }}
        </template>
      </rpa-hint-icon>
    </div>
    <rpa-hint-icon
      :name="sidebarWide ? 'sidebar-wide' : 'sidebar-narrow'"
      :title="sidebarWide ? '切换到窄版' : '切换到宽版'"
      enable-hover-bg
      width="16px"
      height="16px"
      @click="() => (sidebarWide = !sidebarWide)"
    />
  </div>
</template>

<style lang="scss">
.pythonDependence_header {
  margin-bottom: 10px;
  gap: 10px;

  .python-header-title {
    height: 22px;
    font-size: 16px;
    font-weight: 600;
    line-height: 19px;
  }

  .pythonDependence-right {
    .pythonDependence-plus {
      height: 24px;
      font-size: 12px;
      font-weight: 400;
      line-height: 24px;
    }
  }
}

.ant-select-tree li .ant-select-tree-node-content-wrapper {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowarp;
}

.ant-select-tree li span.ant-select-tree-switcher {
  margin-top: -20px;
}

.ant-select-tree {
  padding: 2px 4px;
}

.ant-select-tree li {
  margin: 2px 0;
}
</style>
