<!-- @format -->

# Astron Browser Plugin API 文档

## 1. 概述

- **插件简介**：Astron Browser Plugin是Astron RPA 在web自动化的重要组成部分，为Astron RPA提供Chrome/Edge/Firefox 等浏览器提供网页自动化能力
- **主要特性**：

* 浏览器Tab 页操作
* 网页元素操作
* Cookie 操作
* 脚本注入操作
* iframe 操作

- **版本信息**：5.2.11

## 2. 快速开始

- **安装**：npm run build 打包后使用浏览器插件管理加载插件
- **基础配置**：Chrome 浏览器，node 环境推荐 node版本 v20+

## 3. API 参考

- **接口：http://127.0.0.1:{port}/browser/transition** 默认port: 9082
- **类型：POST**
- **请求体:application/json**

```json
{
  "browser_type": "chrome", // firefox, edge ...
  "data": {
    "x": 854, "y": 314
  },
  "key": "getElement"
}
```

### 3.1 支持的API列表

#### Tab 页操作 (Tab Operations)

- `reloadTab` - 刷新当前标签页
- `stopLoad` - 停止加载
- `openNewTab` - 打开新标签页
- `closeTab` - 关闭标签页
- `updateTab` - 更新标签页 URL
- `activeTab` - 激活标签页
- `getActiveTab` - 获取活跃标签页
- `switchTab` - 切换到指定标签页
- `getAllTabs` - 获取所有标签页
- `backward` - 后退
- `forward` - 前进
- `maxWindow` - 最大化窗口
- `minWindow` - 最小化窗口
- `getTitle` - 获取标签页标题
- `getUrl` - 获取标签页 URL
- `captureScreen` - 网页可视区域截图
- `capturePage` - 截取全部网页
- `loadComplete` - 判断网页是否加载完成
- `getFrames` - 获取所有帧
- `getExtFrames` - 获取扩展帧
- `resetZoom` - 重置缩放
- `getTabId` - 获取标签页 ID
- `getFrameTree` - 获取帧树
- `printPage` - 打印页面

#### 元素操作 (Element Operations)

- `getElement` - 获取元素信息
- `getElementPos` - 获取元素绝对位置
- `checkElement` - 校验元素
- `getOuterHTML` - 获取元素 HTML
- `scrollIntoView` - 滚动到可视区域
- `scrollToTop` - 滚动到顶部
- `elementIsRender` - 等待元素渲染
- `elementIsReady` - 元素是否准备好（包含页面状态）

#### 元素属性操作 (Element Attribute Operations)

- `getElementText` - 获取元素文本
- `getElementAttrs` - 获取元素属性
- `setElementAttr` - 设置元素属性
- `removeElementAttr` - 移除元素属性
- `getElementChecked` - 获取元素 checked 状态
- `setElementChecked` - 设置元素 checked 状态
- `getElementSelected` - 获取元素 selected 状态
- `setElementSelected` - 设置元素 selected 状态

#### 元素交互 (Element Interaction)

- `clickElement` - 点击元素
- `inputElement` - 输入内容

#### 元素选择与导航 (Element Selection & Navigation)

- `similarElement` - 获取相似元素
- `elementFromSelect` - 通过选择条件获取元素
- `getSimilarIterator` - 相似元素迭代
- `getParentElement` - 获取父元素（扩大选区）
- `getChildElement` - 获取子元素（缩小选区）
- `getRelativeElement` - 获取关联元素（parent/sibling/child）
- `generateElement` - 通过 xpath/cssSelector/text 生成元素

#### 数据抓取 (Data Extraction)

- `elementIsTable` - 判断元素是否为表格
- `tableDataBatch` - 批量抓取表格数据
- `tableColumnDataBatch` - 批量抓取表格单列数据
- `tableHeaderBatch` - 批量抓取表头数据
- `similarBatch` - 批量抓取相似元素数据
- `simalarListBatch` - 批量抓取相似元素列表
- `highLightColumn` - 高亮列
- `getBatchData` - 获取批量数据
- `scrollWindow` - 滚动窗口
- `elementShot` - 元素截图
- `getTableData` - 获取表格数据

#### JavaScript 执行 (JavaScript Execution)

- `runJS` - 注入并执行 JavaScript 代码

#### Cookie 操作 (Cookie Operations)

- `getCookie` - 获取 cookie
- `setCookies` - 设置 cookie
- `removeCookie` - 删除 cookie

#### 调试器控制 (Debugger Control)

- `startDebugger` - 启动调试器
- `stopDebugger` - 停止调试器

#### 网络监听 (Network Monitoring)

- `getRequestInterceptionFilters` - 获取请求拦截过滤器
- `setRequestInterceptionFilters` - 设置请求拦截过滤器
- `addRequestInterceptionFilter` - 添加请求拦截过滤器
- `removeRequestInterceptionFilter` - 移除请求拦截过滤器
- `startDebugNetworkListen` - 启动网络监听
- `stopDebugNetworkListen` - 停止网络监听
- `getDebugNetworkData` - 获取网络监听数据
- `clearDebugNetworkData` - 清除网络监听数据

#### 其他操作 (Other Operations)

- `currentExtension` - 获取插件信息
- `backgroundInject` - 后台注入检查 `deprecated`
- `contentInject` - 内容注入检查 `deprecated`

### 3.2 响应格式

- **返回体:application/json**

```json
{
  "code": "0000", // background code 
  "msg": "ok",
  "data": {
    "code": "0000", // content code 
    "data": {
      "matchTypes": [],
      "checkType": "visualization",
      "xpath": "//textarea[@id=\"APjFqb\"]",
      "cssSelector": "#APjFqb",
      "pathDirs": [
        {
          "tag": "textarea",
          "checked": true,
          "value": "textarea",
          "attrs": [
            {
              "name": "id",
              "value": "APjFqb",
              "checked": true,
              "type": 0
            },
            {
              "name": "class",
              "value": "gLFyf",
              "checked": false,
              "type": 1
            },
            {
              "name": "title",
              "value": "Google 搜索",
              "checked": false,
              "type": 0
            }
          ]
        }
      ],
      "rect": {
        "left": 594,
        "top": 268,
        "width": 672,
        "height": 75,
        "right": 1265,
        "bottom": 343,
        "x": 594,
        "y": 268
      },
      "url": "https://www.google.com.hk/",
      "shadowRoot": false,
      "tag": "输入域",
      "text": "unknown",
      "tabTitle": "Google",
      "tabUrl": "https://www.google.com.hk/",
      "isFrame": false,
      "frameId": 0
    },
    "msg": "success"
  }
}
```

### 3.3 API 使用示例

#### Tab 页操作示例

```json
// 获取活跃标签页
{
    "browser_type": "chrome",
    "data": {},
    "key": "getActiveTab"
}

// 打开新标签页
{
    "browser_type": "chrome",
    "data": { "url": "https://www.baidu.com/" },
    "key": "openNewTab"
}

// 获取标签页 URL
{
    "browser_type": "chrome",
    "data": {},
    "key": "getUrl"
}

// 获取标签页 title
{
    "browser_type": "chrome",
    "data": {},
    "key": "getTitle"
}

// 刷新标签页
{
    "browser_type": "chrome",
    "data": {},
    "key": "reloadTab"
}

// 停止加载
{
    "browser_type": "chrome",
    "data": {},
    "key": "stopLoad"
}

// 最大化窗口
{
    "browser_type": "chrome",
    "data": {},
    "key": "maxWindow"
}

// 最小化窗口
{
    "browser_type": "chrome",
    "data": {},
    "key": "minWindow"
}

// 后退
{
    "browser_type": "chrome",
    "data": {},
    "key": "backward"
}

// 前进
{
    "browser_type": "chrome",
    "data": {},
    "key": "forward"
}

// 关闭标签页
{
    "browser_type": "chrome",
    "data": { "url": "https://developer.mozilla.org/zh-CN/plus" },
    "key": "closeTab"
}

// 切换到指定标签页（通过URL）
{
    "browser_type": "chrome",
    "data": { "url": "https://developer.mozilla.org/zh-CN/plus" },
    "key": "switchTab"
}

// 切换到指定标签页（通过标题）
{
    "browser_type": "chrome",
    "data": { "title": "MDN Plus" },
    "key": "switchTab"
}

// 更新标签页 URL
{
    "browser_type": "chrome",
    "data": { "url": "https://www.abc.com" },
    "key": "updateTab"
}

// 网页可视区域截图
{
    "browser_type": "chrome",
    "data": {},
    "key": "captureScreen"
}

// 截取全部网页
{
    "browser_type": "chrome",
    "data": {},
    "key": "capturePage"
}

// 页面是否加载完成
{
    "browser_type": "chrome",
    "data": {},
    "key": "loadComplete"
}

// 获取所有帧
{
    "browser_type": "chrome",
    "data": {},
    "key": "getFrames"
}

// 获取帧树
{
    "browser_type": "chrome",
    "data": {},
    "key": "getFrameTree"
}

// 重置缩放
{
    "browser_type": "chrome",
    "data": {},
    "key": "resetZoom"
}

// 打印页面
{
    "browser_type": "chrome",
    "data": {
        "orientation": "portrait",
        "margins": { "left": 0, "top": 0, "right": 0, "bottom": 0 }
    },
    "key": "printPage"
}
```

#### JavaScript 执行示例

```json
// 注入并执行 JavaScript
{
    "browser_type": "chrome",
    "data": {
        "code": "console.log(1);return 1",
        "url": "http://192.168.56.1:9010/aa/2.html?a=1",
        "tabUrl": "http://192.168.56.1:9010/1.html",
        "iframeXpath": "html/body/div[1]/iframe/html/body/div/button",
        "isFrame": true
    },
    "key": "runJS"
}
```

#### 元素选择和获取示例

```json
// 获取元素信息
{
    "browser_type": "chrome",
    "data": { "x": 854, "y": 314 },
    "key": "getElement"
}

// 获取元素绝对位置
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"app\"]/div/div/div[3]",
        "cssSelector": "#app>div.arrange>div:nth-child(1)>div:nth-child(3)"
    },
    "key": "getElementPos"
}

// 校验元素
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"abc\"]",
        "cssSelector": "#abc"
    },
    "key": "checkElement"
}

// 滚动元素到可视区域
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"abc\"]",
        "cssSelector": "#abc"
    },
    "key": "scrollIntoView"
}

// 等待元素渲染
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"abc\"]",
        "cssSelector": "#abc"
    },
    "key": "elementIsRender"
}

// 元素是否准备好（包含页面状态）
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"container\"]/div[3]/div[2]/div/div[2]/div[1]/p[23]",
        "cssSelector": "p:nth-child(23)"
    },
    "key": "elementIsReady"
}

// 获取元素 HTML
{
    "browser_type": "chrome",
    "data": { "x": 0, "y": 0 },
    "key": "getOuterHTML"
}

// 获取相似元素
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//ul[@id=\"hotsearch-content-wrapper\"]/li[2]/a/span[2]",
        "cssSelector": "#hotsearch-content-wrapper>li:nth-child(2)>a:nth-child(1)>span:nth-child(4)"
    },
    "key": "similarElement"
}

// 通过选择条件获取元素信息
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/div[1]/div[1]/section[5]/section[1]/div/div/button/span",
        "cssSelector": "#app>div:nth-child(3)>div>div:nth-child(2)>section:nth-child(1)>article>div:nth-child(3)>div:nth-child(1)>section:nth-child(5)>section:nth-child(1)>div>div>button>span"
    },
    "key": "elementFromSelect"
}

// 获取父元素（扩大选区）
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"spa-mount-point\"]/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div",
        "cssSelector": "#spa-mount-point>div>div.ent-resource>div>div.ent-resource-main>div.ent-resource-body>div.branch-tabs-wrap>div.tabs-container>div.branch-tabs>div.el-tabs__header>div>div"
    },
    "key": "getParentElement"
}

// 获取子元素（缩小选区）
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"spa-mount-point\"]/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div",
        "cssSelector": "#spa-mount-point>div>div.ent-resource>div>div.ent-resource-main>div.ent-resource-body>div.branch-tabs-wrap>div.tabs-container>div.branch-tabs>div.el-tabs__header>div>div",
        "originXpath": "/html/body/div/section/section/main/div/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div"
    },
    "key": "getChildElement"
}

// 通过 xpath/cssSelector/text 生成元素
{
    "browser_type": "chrome",
    "data": {
        "type": "xpath",
        "value": "//div",
        "returnType": "single"
    },
    "key": "generateElement"
}

// 获取关联元素
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"element\"]",
        "relativeOptions": {
            "relativeType": "child",
            "elementGetType": "index",
            "index": 1
        }
    },
    "key": "getRelativeElement"
}

// 相似元素迭代
{
    "browser_type": "chrome",
    "data": {
        "index": 0,
        "count": 5,
        "xpath": "//nav[@id=\"nav\"]/ul/li[24]/ul/li/a",
        "cssSelector": "#nav>ul>li:nth-child(24)>ul>li>a"
    },
    "key": "getSimilarIterator"
}
```

#### 元素属性操作示例

```json
// 获取元素文本
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"abc\"]",
        "cssSelector": "#abc"
    },
    "key": "getElementText"
}

// 获取元素属性
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"abc\"]",
        "cssSelector": "#abc"
    },
    "key": "getElementAttrs"
}

// 设置元素属性
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"abc\"]",
        "cssSelector": "#abc",
        "attrName": "data-value",
        "attrValue": "test"
    },
    "key": "setElementAttr"
}

// 移除元素属性
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"abc\"]",
        "cssSelector": "#abc",
        "attrName": "data-value"
    },
    "key": "removeElementAttr"
}

// 获取 checked 状态
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//input[@id=\"checkbox\"]",
        "cssSelector": "#checkbox"
    },
    "key": "getElementChecked"
}

// 设置 checked 状态
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//input[@id=\"checkbox\"]",
        "cssSelector": "#checkbox",
        "checked": true
    },
    "key": "setElementChecked"
}

// 获取 selected 状态
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//option[@value=\"option1\"]",
        "cssSelector": "option[value='option1']"
    },
    "key": "getElementSelected"
}

// 设置 selected 状态
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//option[@value=\"option1\"]",
        "cssSelector": "option[value='option1']",
        "selected": true
    },
    "key": "setElementSelected"
}
```

#### 元素交互示例

```json
// 点击元素
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//button[@id=\"submit\"]",
        "cssSelector": "#submit"
    },
    "key": "clickElement"
}

// 输入内容
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//input[@id=\"username\"]",
        "cssSelector": "#username",
        "text": "test_input"
    },
    "key": "inputElement"
}
```

#### Cookie 操作示例

```json
// 获取 Cookie
{
    "browser_type": "chrome",
    "data": {
        "url": "http://localhost:1420/",
        "name": "JSESSIONID"
    },
    "key": "getCookie"
}

// 设置 Cookie
{
    "browser_type": "chrome",
    "data": {
        "url": "http://localhost:1420/",
        "name": "JSESSIONID",
        "value": "123"
    },
    "key": "setCookies"
}

// 删除 Cookie
{
    "browser_type": "chrome",
    "data": {
        "url": "http://localhost:1420/",
        "name": "JSESSIONID"
    },
    "key": "removeCookie"
}
```

#### 数据抓取示例

```json
// 判断元素是否为表格
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//table[@id=\"dataTable\"]",
        "cssSelector": "#dataTable"
    },
    "key": "elementIsTable"
}

// 批量抓取表格数据
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/section[3]/table[1]/tbody/tr[5]/td[1]",
        "cssSelector": "#app>div:nth-child(3)>div.ant-row.css-9loccf>div:nth-child(2)>section:nth-child(1)>article>section:nth-child(4)>table:nth-child(4)>tbody>tr:nth-child(5)>td:nth-child(1)"
    },
    "key": "tableDataBatch"
}

// 批量抓取表格单列数据
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/section[3]/table[1]/tbody/tr[5]/td[1]",
        "cssSelector": "#app>div:nth-child(3)>div.ant-row.css-9loccf>div:nth-child(2)>section:nth-child(1)>article>section:nth-child(4)>table:nth-child(4)>tbody>tr:nth-child(5)>td:nth-child(1)"
    },
    "key": "tableColumnDataBatch"
}

// 批量抓取相似元素数据
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/section[3]/table[1]/tbody/tr[5]/td[1]",
        "cssSelector": "#app>div:nth-child(3)>div.ant-row.css-9loccf>div:nth-child(2)>section:nth-child(1)>article>section:nth-child(4)>table:nth-child(4)>tbody>tr:nth-child(5)>td:nth-child(1)"
    },
    "key": "similarBatch"
}

// 元素截图
{
    "browser_type": "chrome",
    "data": {
        "xpath": "//div[@id=\"container\"]/div[3]/div[2]/div/div[2]/div[1]/p[23]",
        "cssSelector": "p:nth-child(23)"
    },
    "key": "elementShot"
}

// 滚动窗口
{
    "browser_type": "chrome",
    "data": {
        "scrollX": 0,
        "scrollY": 100
    },
    "key": "scrollWindow"
}
```

#### 调试器和网络监听示例

```json
// 启动调试器
{
    "browser_type": "chrome",
    "data": {},
    "key": "startDebugger"
}

// 停止调试器
{
    "browser_type": "chrome",
    "data": {},
    "key": "stopDebugger"
}

// 获取请求拦截过滤器
{
    "browser_type": "chrome",
    "data": {},
    "key": "getRequestInterceptionFilters"
}

// 设置请求拦截过滤器
{
    "browser_type": "chrome",
    "data": {
        "filters": [
            { "urlPattern": ".*\\.js$", "pathPattern": "static" }
        ]
    },
    "key": "setRequestInterceptionFilters"
}

// 启动网络监听
{
    "browser_type": "chrome",
    "data": {
        "filters": [
            { "urlPattern": ".*api.*", "pathPattern": "" }
        ]
    },
    "key": "startDebugNetworkListen"
}

// 停止网络监听
{
    "browser_type": "chrome",
    "data": {},
    "key": "stopDebugNetworkListen"
}

// 获取网络监听数据
{
    "browser_type": "chrome",
    "data": {},
    "key": "getDebugNetworkData"
}

// 清除网络监听数据
{
    "browser_type": "chrome",
    "data": {},
    "key": "clearDebugNetworkData"
}
```

#### 其他操作示例

```json
// 获取插件信息
{
    "browser_type": "chrome",
    "data": {},
    "key": "currentExtension"
}

// 后台注入检查
{
    "browser_type": "chrome",
    "data": {},
    "key": "backgroundInject"
}

// 内容注入检查
{
    "browser_type": "chrome",
    "data": {},
    "key": "contentInject"
}
```

## 4. 调用示例

```
curl -X POST 'http://127.0.0.1:9082/browser/transition' -H 'User-Agent: Reqable/2.30.3' -H 'Content-Type: application/json' -d '{
  "browser_type": "<<bt>>",
  "data": {
    "x": 0,
    "y": 0
  },
  "key": "getElement"
}'
```

## 5. 高级配置与集成

针对市面常见浏览器，可自行适配对应的浏览器名称与token，一般为浏览器可执行文件的文件名称

## 6. 注意事项

- 插件通信依靠Astron RPA 客户端服务，请先打开Astron RPA 客户端
- 插件通信依靠注册的token,token 会编码，例如Chrome 浏览器 token=`$chrome$`

## 7. 常见问题解答

- 不同浏览器使用插件执行时需要对应能力支持该浏览器。

## 8. 附录

- **错误码列表**：

```
  SUCCESS = '0000', // 成功
  UNKNOWN_ERROR = '5001', // 未知异常
  ELEMENT_NOT_FOUND = '5002', // 元素未找到
  EXECUTE_ERROR = '5003', // 执行错误
  VERSION_ERROR = '5004', // 版本错误
```
