<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

import { ROBOT_EDITING, ROBOT_LOCKED, ROBOT_ONSHELF, ROBOT_PUBLISHED } from '@/constants/resource'

defineProps({
  type: {
    type: String,
    default: 'default',
  },
})

// 已更新
const MYPUBLISH_APPSTATUS_UPDATED = 'updated'
// 未更新
const MYPUBLISH_APPSTATUS_UNUPDATED = 'unupdated'

const { t } = useTranslation()

const renderStatus = computed(() => ({
  success: {
    text: t('common.planCompleted'),
    color: 'green',
  },
  exe_error: {
    text: t('common.executionFailed'),
    color: 'red',
  },
  cancel: {
    text: t('common.planAborted'),
    color: 'yellow',
  },
  start_error: {
    text: t('common.startFailed'),
    color: 'grey',
  },
  executing: {
    text: t('common.executing'),
    color: 'blue',
  },
  robotSuccess: {
    text: t('common.success'),
    color: 'green',
  },
  robotFail: {
    text: t('common.fail'),
    color: 'red',
  },
  robotCancel: {
    text: t('common.robotCancel'),
    color: 'yellow',
  },
  robotExecute: {
    text: t('common.robotExecute'),
    color: 'blue',
  },
  // notExecuted: {
  //   text: t('common.notExecuted'),
  //   color: 'grey',
  // },
  publish: {
    text: t('common.released'),
    color: 'green',
  },
  unpublish: {
    text: t('common.unpublished'),
    color: 'orange',
  },
  enable: {
    text: t('common.enable'),
    color: 'yellow',
  },
  [MYPUBLISH_APPSTATUS_UPDATED]: {
    text: t('common.updated'),
    color: 'green',
  },
  [MYPUBLISH_APPSTATUS_UNUPDATED]: {
    text: t('common.unupdated'),
    color: 'grey',
  },
  [ROBOT_EDITING]: {
    text: t('common.editing'),
    color: 'blue',
  },
  [ROBOT_PUBLISHED]: {
    text: t('common.released'),
    color: 'green',
  },
  [ROBOT_ONSHELF]: {
    text: t('common.published'),
    color: 'green',
  },
  [ROBOT_LOCKED]: {
    text: t('common.locked'),
    color: 'grey',
  },
  default: {
    text: '',
    color: 'grey',
  },
}))
</script>

<template>
  <div class="StatusCircle">
    <span :class="`circle StatusCircle-${renderStatus[type || 'default']?.color}`" />
    <span>{{ renderStatus[type || 'default']?.text }}</span>
  </div>
</template>

<style lang="scss" scoped>
.StatusCircle {
  display: inline-block;

  .circle {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 10px;
  }

  &-grey {
    background-color: #a5a4ac;
  }
  &-grayText {
    color: #a5a4ac;
  }

  &-red {
    background-color: #ec483e;
  }
  &-redText {
    color: #ec483e;
  }

  &-blue {
    background-color: var(--color-primary);
  }
  &-blueText {
    color: var(--color-primary);
  }

  &-green {
    background-color: #2fcb64;
  }
  &-greenText {
    color: #2fcb64;
  }

  &-lime {
    background-color: #a0d911;
  }
  &-limeText {
    color: #a0d911;
  }

  &-yellow {
    background-color: #eccd00;
    color: #eccd00;
  }
  &-yellowText {
    color: #eccd00;
  }

  &-orange {
    background-color: #f39d09;
  }
  &-orangeText {
    color: #f39d09;
  }
}
</style>
