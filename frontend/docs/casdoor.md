# Casdoor 认证说明

## 认证流程

### 登录检测

- 通过 [`casdoorLoginStatus`](../packages/web-app/src/auth/authApi.ts) 检查当前用户是否已登录。
- 未登录时自动跳转到 Casdoor 登录页面。

### 登录跳转

- 调用 [`casdoorLoginUrl`](../packages/web-app/src/auth/authApi.ts) 获取 Casdoor 登录地址。
- 支持自定义回调地址（`redirect_uri`），登录后自动跳转回前端。

### 登录回调处理

- 登录后 Casdoor 回调带有 `code` 和 `state` 参数。
- 前端通过 [`casdoorSignin`](../packages/web-app/src/auth/authApi.ts) 接口将 `code`、`state` 发送到后端换取用户信息，后端set-cookie响应头携带cookie，路由组件将保存cookie。

### 登出

- 调用 [`casdoorSignout`](../packages/web-app/src/auth/authApi.ts) 注销登录，清理本地信息并跳转到首页。

### 鉴权与会话过期

- 所有接口请求都经过路由组件，都会带上cookie
- 若后端返回 code 为 `900001`，自动跳转到登录页面重新认证。

## 主要方法说明

- [`login()`](../packages/web-app/src/auth/casdoor.auth.ts)：主登录入口，自动处理回调和跳转。
- [`logout()`](../packages/web-app/src/auth/casdoor.auth.ts)：登出并清理本地信息。
- [`getUserName()`](../packages/web-app/src/auth/casdoor.auth.ts)：获取当前登录用户名。
- [`checkLogin(callback)`](../packages/web-app/src/auth/casdoor.auth.ts)：检测登录状态，未登录时自动跳转登录。
- [`checkHttpResponse(response)`](../packages/web-app/src/auth/casdoor.auth.ts)：检测接口返回是否登录过期。

## 依赖与约定

- cookie 由后端接口返回，并由路由组件存储，后续请求需带上。
- 登录、登出、会话过期等流程均有自动跳转处理。
