<script setup lang="ts">
import { onMounted, provide, ref } from 'vue'

import Header from '@/components/Header.vue'
import Register from '@/components/LoginComponents/Register/Index.vue'
import SelfLogin from '@/components/LoginComponents/Self/Index.vue'
import TenantList from '@/components/LoginComponents/TenantList/Index.vue'
import { windowManager } from '@/platform'
import { useUserStore } from '@/stores/useUserStore'

const userStore = useUserStore()

// 登录类型
function toggleLoginType(type: string) {
  userStore.setLoginType(type)
}

// 登录步骤, 登录-> 选择租户
const loginStep = ref('login')
function loginStepFn(type: string) {
  loginStep.value = type
}
// 提供选择租户的注入
provide('loginStepFn', loginStepFn)

onMounted(() => {
  windowManager.restoreLoginWindow()
})
</script>

<template>
  <div class="login-container bg-no-repeat bg-cover padT60">
    <Header :maximize="false" />
    <div v-if="loginStep === 'login'" class="login-type-container">
      <div v-if="userStore.loginType === 'self'" class="login-self-container">
        <SelfLogin @toggle-login-type="toggleLoginType" />
      </div>
    </div>
    <div v-if="loginStep === 'register'" class="login-register-container">
      <Register />
    </div>
    <div v-if="loginStep === 'tenant'" class="login-tenant-container">
      <TenantList />
    </div>
  </div>
</template>

<style lang="scss">
.login-container {
  inset: 0;
  background-image: var(--loginBg);
  height: 100%;
  background-color: #ffffff;
  --headerZindex: 100;
}

.login-self-container {
  inset: 0;
  // animation: fadeIn .3s;
}

.login-third-container {
  position: absolute;
  inset: 0;
  z-index: calc(var(--headerZindex) + 1);
  background-image: var(--loginOpenBg);
  // animation: fadeIn .3s;
}

.login-tenant-container {
  inset: 0;
}
.login-register-container {
  inset: 0;
}

.box-main {
  display: flex;
  flex-direction: column;
  // justify-content: center;
  align-items: center;
  font-size: 22px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 1px 1px 18px 2px rgb(99 127 150 / 23%);
  padding: 16px;
}

.Login {
  display: flex;
  justify-content: space-evenly;
  align-content: center;
  user-select: none;

  &-left {
    width: 45%;
    height: 400px;
    display: flex;
    justify-content: center;
    align-items: center;

    & p {
      padding-top: 15px;
      margin-top: 10px;
    }
  }

  &-right {
    &_form {
      width: 100%;

      .ant-form-explain {
        text-align: left;
      }
    }

    &_register {
      float: right;
      height: 40px;
      margin-top: -10px;
      color: $color-primary;
    }
  }

  &-right-open {
    width: 620px;
  }

  &-offline-box {
    height: 358px;
    padding: 26px 24px;
    box-sizing: border-box;
  }

  .ant-tabs.ant-tabs-card .ant-tabs-card-bar .ant-tabs-tab {
    border: none;
    background: none;
    padding: 0 0px 0px 0px;
    margin-right: 10px;
    height: 36px;
  }

  .ant-tabs-bar {
    border-bottom: none;
  }

  .ant-form-item {
    height: 54px;
    // margin-bottom: 5px;
  }

  .ant-form-explain {
    margin-bottom: -18px;
  }
}

.otherOperation {
  .rememberChecked {
    float: left;
    color: $color-primary;
  }

  a {
    float: right;
    padding-left: 15px;
  }
}

.otherOperationLeft {
  a {
    float: left;
    padding-left: 0;
  }
}

.mobileBindBtn {
  display: flex;
  justify-content: space-between;
}

.codeButton {
  width: 100% !important;
}

.iconColor {
  color: rgba(0, 0, 0, 0.25);
}

.ant-form-item .ant-form-item-explain-error {
  font-size: 12px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}
</style>
