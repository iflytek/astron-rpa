<script setup lang="ts">
import { LeftOutlined, RightOutlined } from '@ant-design/icons-vue'
import { Spin } from 'ant-design-vue'
import { inject, onMounted, ref } from 'vue'

import { getTenanList, sendTenantId } from '@/api/login/login'
import { taskNotify } from '@/api/task'
import { DESIGNER } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import type { resOption } from '@/views/Home/types'

const tenantList = ref([])
const selectId = ref('')
const isChosing = ref(false)
const tenantListLoading = ref(false)

const loginStep = inject('loginStepFn', (...args) => {
  console.log(args)
})

function backToLogin() {
  if (isChosing.value)
    return
  loginStep('login')
}

function chooseTenantPreFn(item) {
  sendTenantId({ tenantId: item.id }).then(() => {
    useRoutePush({ name: DESIGNER })
    selectId.value = item.id
    taskNotify({ event: 'login' })
  })
  if (isChosing.value)
    return
  isChosing.value = true
}

onMounted(() => {
  getTenanListFn()
})

function getTenanListFn() {
  tenantListLoading.value = true
  getTenanList().then((res: resOption) => {
    tenantList.value = res.data.tenantDtos
    tenantListLoading.value = false
  })
}
</script>

<template>
  <div class=" self-container box-main">
    <div class="LoginBox">
      <div class="LoginBox-offline offline-back" @click="backToLogin">
        <LeftOutlined />
        {{ $t("goBack") }}
      </div>
      <div class="LoginBox-tenantTitle">
        {{ $t("selectSpace") }}
      </div>
      <div class="title-grey">
        {{ $t("spaceInfo") }}
      </div>
      <div class="tenant-list">
        <div class="tenant-list-box">
          <div v-if="tenantListLoading" class="tenant-list-loading">
            <Spin />
          </div>
          <div v-for="item in tenantList" v-else :key="item.id" class="tenant-list-item" @click="chooseTenantPreFn(item)">
            <div class="tli-one flex_center">
              {{ item.name.substring(0, 1) }}
            </div>
            <span class="tli-name">{{ item.name }}</span>
            <Spin v-if="item.id === selectId" class="tli-icon" size="small" />
            <RightOutlined v-else class="tli-icon" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.self-container {
  position: absolute;
  top: 50%;
  transform: translateY(-45%);
  right: 80px;
  width: 338px;
  height: 380px;
}

.LoginBox {
  width: 100%;
  position: relative;
  text-align: left;
  padding: 0 7.5px;

  &-tenantTitle {
    line-height: 20px;
    font-size: 20px;
    font-weight: 600;
    color: #2c2c31;
    letter-spacing: 0.2px;
  }

  &-offline {
    position: absolute;
    top: -60px;
    font-size: 14px;
    font-weight: 400;
    color: #7b7f9d;
    line-height: 19px;
    letter-spacing: 0.14px;
    user-select: none;
    cursor: pointer;
  }

  .title-grey {
    line-height: 14px;
    font-size: 12px;
    font-weight: 400;
    color: #999999;
    margin-top: 15px;
    letter-spacing: 0.12px;
  }

  .offline-back {
    left: -13px;

    &:hover {
      color: #3f68f6;
    }
  }

  .tenant-list {
    margin-top: 16px;
    height: 259px;
    background: #ffffff;
    border: 1px solid rgba(102, 102, 102, 0.289);
    border-radius: 11px;
    padding: 12px 10px;
    box-sizing: border-box;
    overflow: hidden;
    position: relative;

    .tenant-list-box {
      width: 100%;
      height: 100%;
      overflow-y: auto;
    }

    .tenant-list-item {
      width: 100%;
      height: 48px;
      font-size: 14px;
      border: 1px solid #ffffff;
      border-radius: 7px;
      display: flex;
      align-items: center;
      padding: 9px;
      box-sizing: border-box;
      overflow: hidden;
      position: relative;
      cursor: pointer;

      &:hover {
        background: rgba(104, 138, 248, 0.085);
        color: rgba(60, 104, 246, 1);
        transition: all ease 0.3s;

        .tli-one {
          opacity: 1;
          background: linear-gradient(#3f6af6 0%, #6d8ef8 100%);
        }
      }

      .tli-one {
        width: 29px;
        height: 29px;
        opacity: 0.42;
        background: linear-gradient(#456ef6 0%, #688af8 100%);
        border: 1px solid #ffffff;
        border-radius: 6px;
        font-size: 18px;
        font-weight: 500;
        color: #ffffff;
      }

      .tli-name {
        font-size: 14px;
        margin-left: 10px;
        width: 180px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .tli-icon {
        position: absolute;
        right: 10px;
      }
    }

    .tenant-list-loading {
      position: absolute;
      top: 0%;
      left: 0%;
      width: 100%;
      height: 100%;
      background-color: #ffffff;
      z-index: 9;
      text-align: center;
      padding-top: 20px;
    }
  }
}

.flex_center {
  display: flex;
  justify-content: center;
  align-items: center;
}

.tenant-list-box::-webkit-scrollbar {
  width: 6px;
}

.tenant-list-box::-webkit-scrollbar-thumb {
  background-color: rgb(189, 189, 189);
}
</style>
