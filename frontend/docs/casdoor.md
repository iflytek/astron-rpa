# Casdoor 配置说明文档

## 1. 配置项说明

Casdoor 认证在本项目中通过 SDK 初始化，主要配置项如下：

| 配置项           | 说明                              | 示例值                     |
| ---------------- | --------------------------------- | -------------------------- |
| serverUrl        | Casdoor 服务端地址                | http://localhost:8000      |
| clientId         | 应用 Client ID                    | e3ba6fec42cfe996121f       |
| appName          | Casdoor 应用名称                  | example-app                |
| organizationName | Casdoor 组织名称                  | example-org                |
| redirectPath     | 登录回调路径                      | /                          |
| scope            | 权限范围                          | read                       |
| signinPath       | 登录接口路径                      | /api/robot/user/api/signin |
| backendServerUrl | 后端服务地址,默认本地路由进行转发 | http://localhost:13159     |

配置代码示例（见 [`packages/web-app/src/auth/casdoor.auth.ts`](../packages/web-app/src/auth/casdoor.auth.ts)）：

```typescript
const config = {
  serverUrl: 'http://localhost:8000',
  clientId: 'e3ba6fec42cfe996121f',
  appName: 'example-app',
  organizationName: 'example-org',
  redirectPath: '/',
  scope: 'read',
  signinPath: '/api/robot/user/api/signin',
  backendServerUrl: 'http://localhost:13159',
}
```

## 2. 环境变量配置

通过环境变量（[`.env`](../packages/web-app/.env) 文件）配置 Casdoor 相关参数，示例：

```
VITE_CASDOOR_SERVER_URL=http://localhost:8000
VITE_CASDOOR_CLIENT_ID=e3ba6fec42cfe996121f
VITE_CASDOOR_APP_NAME=example-app
VITE_CASDOOR_ORG=example-org
VITE_CASDOOR_BACKEND_SERVER_URL=http://localhost:13159
VITE_CASDOOR_SIGNIN_PATH=/api/robot/user/api/signin
```

## 3. 登录流程

1. 检查本地是否已登录（`accessToken`）。
2. 未登录时，自动重定向到 Casdoor 登录页面。
3. 登录回调后，获取 `code` 和 `state`，调用后端接口signin换取 `accessToken`存储到本地, 并发送给本地路由组件供路由组件鉴权使用。
4. 登录成功后跳转到主页面。

> 注：
>
> - 后端接口signin(VITE_CASDOOR_BACKEND_SERVER_UR+VITE_CASDOOR_SIGNIN_PATH)：http://localhost:13159/api/robot/user/api/signin
> - 所有 Casdoor 相关操作均依赖本地存储的 `accessToken`，并通过 HTTP Header 传递。

## 4. 其他说明

- 如需修改 Casdoor 配置，请确保同步更新前端 SDK 初始化参数及后端配置文件。
