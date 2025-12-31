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

- **版本信息**：5.2.4

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

```json
// 获取活跃tab
{
    "browser_type": "chrome",
    "data": {"": ""},
    "key": "getActiveTab"
}

// 打开网页
{
    "browser_type": "chrome",
    "data": { "url": "https://www.baidu.com/"},
    "key": "openNewTab"
}

// 注入JS
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

// 校验元素
{
    "browser_type": "chrome",
    "data": {
     "xpath": "//div[@id=\"abc\"]",
      "cssSelector": "#abc",
      ...
    },
    "key": "checkElement"
}
//校验元素返回的也是元素绝对位置

// 滚动到可视区域
{
    "browser_type": "chrome",
    "data": {
      "xpath": "//div[@id=\"abc\"]",
      "cssSelector": "#abc",
      ...
    },
    "key": "scrollIntoView"
}

// 在指定的tab, 指定的frame下执行 code
{
    "browser_type": "chrome",
    "data": {
        "tabUrl": "",
        "url": "",
        "code": "console.log("ok");return "ok";"
    },
    "key": "executeScriptOnFrame"
}
// 最大化窗口
{
    "browser_type": "chrome",
    "data": {
      "url": ""
    },
    "key": "maxWindow"
}

// 获取tab 的Url
{
    "browser_type": "chrome",
    "data": {
      "": ""
    },
    "key": "getUrl"
}
// 获取tab 的 title
{
    "browser_type": "chrome",
    "data": {
      "": ""
    },
    "key": "getTitle"
}
// 网页可视区域截图
{
    "browser_type": "chrome",
    "data": {
      "": ""
    },
    "key": "captureScreen"
}

// 获取元素绝对位置
{
    "browser_type": "chrome",
    "data": {
     "xpath": "//div[@id=\"app\"]/div/div/div[3]",
      "cssSelector": "#app>div.arrange>div:nth-child(1)>div:nth-child(3)",
      ...
    },
    "key": "getElementPos"
}


// 获取cookie
{
    "browser_type": "chrome",
    "data": {
      "url": "http://localhost:1420/",
      "name": "JSESSIONID"
    },
    "key": "getCookie"
}
// 设置cookie
{
    "browser_type": "chrome",
    "data":{
      "url": "http://localhost:1420/",
      "name": "JSESSIONID",
          "value": "123"
    },
    "key": "setCookies"
}
// 删除cookie
{
    "browser_type": "chrome",
    "data":{
      "url": "http://localhost:1420/",
      "name": "JSESSIONID"
    },
    "key": "removeCookie"
}

// 刷新 tab页面
{
    "browser_type": "chrome",
    "data": {
      "": ""
    },
    "key": "reloadTab"
}
// 获取相似元素
{
  "browser_type": "chrome",
  "data": {
   "xpath": "//ul[@id=\"hotsearch-content-wrapper\"]/li[2]/a/span[2]",
    "cssSelector": "#hotsearch-content-wrapper>li:nth-child(2)>a:nth-child(1)>span:nth-child(4)",
    ...
  },
  "key": "similarElement"
}

// 通过元素信息获取元素信息，适用于单元素多元素，用于遍历元素等
{
  "browser_type": "chrome",
   "data": {
      "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/div[1]/div[1]/section[5]/section[1]/div/div/button/span",
      "cssSelector": "#app>div:nth-child(3)>div>div:nth-child(2)>section:nth-child(1)>article>div:nth-child(3)>div:nth-child(1)>section:nth-child(5)>section:nth-child(1)>div>div>button>span",
      ...
    },
  "key": "elementFromSelect"
}
// 返回结果是个元素信息的数组，单元素数组length 为1，多元素则数组length > 1, 若无则返回的是null
{
  "code": "0000",
  "msg": "ok",
  "data": {
    "code": "0000",
    "data": [
      {
        "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/div[1]/div[1]/section[5]/section[1]/div/div[1]/button/span",
        "cssSelector": "#app>div:nth-child(3)>div>div:nth-child(2)>section:nth-child(1)>article>div:nth-child(3)>div:nth-child(1)>section:nth-child(5)>section:nth-child(1)>div>div:nth-child(1)>button>span",
        ...
      },
      {
        "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/div[1]/div[1]/section[5]/section[1]/div/div[2]/button/span",
        "cssSelector": "#app>div:nth-child(3)>div>div:nth-child(2)>section:nth-child(1)>article>div:nth-child(3)>div:nth-child(1)>section:nth-child(5)>section:nth-child(1)>div>div:nth-child(2)>button>span",
        ...
      },
      {
        "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/div[1]/div[1]/section[5]/section[1]/div/div[3]/button/span",
        "cssSelector": "#app>div:nth-child(3)>div>div:nth-child(2)>section:nth-child(1)>article>div:nth-child(3)>div:nth-child(1)>section:nth-child(5)>section:nth-child(1)>div>div:nth-child(3)>button>span",
        ...
      },
      ...
    ],
    "msg": "success"
  }
}
// 等待元素
{
    "browser_type": "chrome",
    "data": {
     "xpath": "//div[@id=\"abc\"]",
      "cssSelector": "#abc",
      ...
    },
    "key": "elementIsRender"
}

// 网页是否加载完成
{
    "browser_type": "chrome",
    "data": {
     "":""
    },
    "key": "loadComplete"
}
// 停止加载
{
    "browser_type": "chrome",
    "data": {"": ""},
    "key": "stopLoad"
}

// backward
{
    "browser_type": "chrome",
    "data": { "": ""},
    "key": "backward"
}
// forward
{
    "browser_type": "chrome",
    "data": { "": ""},
    "key": "forward"
}

// 关闭网页
{
    "browser_type": "chrome",
    "data": { "url": "https://developer.mozilla.org/zh-CN/plus"},
    "key": "closeTab"
}
// 切换到指定页面
{
    "browser_type": "chrome",
    "data": { "url": "https://developer.mozilla.org/zh-CN/plus"},
    "key": "switchTab"
}
{
    "browser_type": "chrome",
    "data": { "title": "MDN Plus"},
    "key": "switchTab"
}

// 截取全部网页
{
  "browser_type": "chrome",
  "data": {
      "": ""
   },
  "key": "capturePage"
}

// 数据抓取表格
{
  "browser_type": "chrome",
  "data": {
      "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/section[3]/table[1]/tbody/tr[5]/td[1]",
      "cssSelector": "#app>div:nth-child(3)>div.ant-row.css-9loccf>div:nth-child(2)>section:nth-child(1)>article>section:nth-child(4)>table:nth-child(4)>tbody>tr:nth-child(5)>td:nth-child(1)",
     ...
    },
  "key": "tableDataBatch"
}

// 数据抓取表格单列
{
  "browser_type": "chrome",
  "data": {
      "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/section[3]/table[1]/tbody/tr[5]/td[1]",
      "cssSelector": "#app>div:nth-child(3)>div.ant-row.css-9loccf>div:nth-child(2)>section:nth-child(1)>article>section:nth-child(4)>table:nth-child(4)>tbody>tr:nth-child(5)>td:nth-child(1)",
      ...
    },
  "key": "tableColumnDataBatch"
}

// 数据抓取 相似元素
{
  "browser_type": "chrome",
  "data": {
      "xpath": "//div[@id=\"app\"]/div[2]/div/div[2]/section[1]/article/section[3]/table[1]/tbody/tr[5]/td[1]",
      "cssSelector": "#app>div:nth-child(3)>div.ant-row.css-9loccf>div:nth-child(2)>section:nth-child(1)>article>section:nth-child(4)>table:nth-child(4)>tbody>tr:nth-child(5)>td:nth-child(1)",
      ...
    },
  "key": "similarBatch"
}
// 更新当前tab, 更新当前tab 地址为 url 地址
{
  "browser_type": "chrome",
  "data": {
      "url": "https://www.abc.com"
  },
  "key": "updateTab"
}
// elementShot 元素截图
{
  "browser_type": "chrome",
  "data": {
      "xpath": "//div[@id=\"container\"]/div[3]/div[2]/div/div[2]/div[1]/p[23]",
      "cssSelector": "p:nth-child(23)",
     ...
    },
  "key": "elementShot"
}

// elementIsReady 元素是否准备好了，包含页面状态
{
  "browser_type": "chrome",
   "data": {
      "xpath": "//div[@id=\"container\"]/div[3]/div[2]/div/div[2]/div[1]/p[23]",
      "cssSelector": "p:nth-child(23)",
      ...
    },
  "key": "elementIsReady"
}

// 相似元素迭代
{
  "browser_type": "chrome",
   "data": {
      "index": 0,
      "count": 5,
      "xpath": "//nav[@id=\"nav\"]/ul/li[24]/ul/li/a",
      "cssSelector": "#nav>ul>li:nth-child(24)>ul>li>a",
      ...
    },
  "key": "getSimilarIterator"
}
// 返回结果
{
  "code": "0000",
  "msg": "ok",
  "data": {
    "code": "0000",
    "data": [{
      "index": 0,
      "count": 5,
      "xpath": "//nav[@id=\"nav\"]/ul/li[24]/ul/li[13]/a",
      "cssSelector": "#nav>ul>li:nth-child(24)>ul>li:nth-child(13)>a",
      ...
      "similarCount": 15
    },
    ...
    ],
    "msg": "success"
  }
}

// 获取元素html
{
   "browser_type": "chrome",
    "data": {
      "x": 0,
      "y": 0
    },
    "key": "getOuterHTML"
}
// 返回结果
{
  "code": "0000",
  "msg": "ok",
  "data": {
    "code": "0000",
    "data": {
      "matchTypes": [],
      "checkType": "visualization",
      "xpath": "//div[@id=\"spa-mount-point\"]/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div",
      "cssSelector": "#spa-mount-point>div>div.ent-resource>div>div.ent-resource-main>div.ent-resource-body>div.branch-tabs-wrap>div.tabs-container>div.branch-tabs>div.el-tabs__header>div>div",
      "abXpath": "/html/body/div/section/section/main/div/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div",
      "outerHTML": "<div class=\"el-tabs__nav-scroll\"><div role=\"tablist\" class=\"el-tabs__nav is-top\" style=\"transform: translateX(0px);\"><div class=\"el-tabs__active-bar is-top\" style=\"width: 85px; transform: translateX(0px);\"></div><div id=\"tab-active\" aria-controls=\"pane-active\" role=\"tab\" aria-selected=\"true\" tabindex=\"0\" class=\"el-tabs__item is-top is-active\"><span data-v-7a2ea2be=\"\"><span data-v-7a2ea2be=\"\">活跃分支 </span><span data-v-23817c3f=\"\" data-v-7a2ea2be=\"\" class=\"count active\">4</span></span></div><div id=\"tab-my\" aria-controls=\"pane-my\" role=\"tab\" tabindex=\"-1\" class=\"el-tabs__item is-top\"><span data-v-7a2ea2be=\"\"><span data-v-7a2ea2be=\"\">我的分支 </span><span data-v-23817c3f=\"\" data-v-7a2ea2be=\"\" class=\"count\">5</span></span></div><div id=\"tab-all\" aria-controls=\"pane-all\" role=\"tab\" tabindex=\"-1\" class=\"el-tabs__item is-top\"><span data-v-7a2ea2be=\"\"><span data-v-7a2ea2be=\"\">全部分支 </span><span data-v-23817c3f=\"\" data-v-7a2ea2be=\"\" class=\"count\">5</span></span></div><div id=\"tab-lazy\" aria-controls=\"pane-lazy\" role=\"tab\" tabindex=\"-1\" class=\"el-tabs__item is-top\"><span data-v-7a2ea2be=\"\"><span data-v-7a2ea2be=\"\">非活跃分支 </span><span data-v-23817c3f=\"\" data-v-7a2ea2be=\"\" class=\"count\">1</span></span></div></div></div>"
    },
    "msg": "success"
  }
}
// 获取元素的父元素，扩大选区
{
   "browser_type": "chrome",
    "data": {
      "matchTypes": [],
      "checkType": "visualization",
      "xpath": "//div[@id=\"spa-mount-point\"]/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div",
      "cssSelector": "#spa-mount-point>div>div.ent-resource>div>div.ent-resource-main>div.ent-resource-body>div.branch-tabs-wrap>div.tabs-container>div.branch-tabs>div.el-tabs__header>div>div",
      "abXpath": "/html/body/div/section/section/main/div/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div",
      ...
    },
    "key": "getParentElement"
}

// 获取元素的子元素，缩小选取
{
  "browser_type": "chrome",
  "data": {
      "matchTypes": [],
      "checkType": "visualization",
      "xpath": "//div[@id=\"spa-mount-point\"]/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div",
      "cssSelector": "#spa-mount-point>div>div.ent-resource>div>div.ent-resource-main>div.ent-resource-body>div.branch-tabs-wrap>div.tabs-container>div.branch-tabs>div.el-tabs__header>div>div",
      "abXpath": "/html/body/div/section/section/main/div/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div",
      "originXpath": "/html/body/div/section/section/main/div/div/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div", // 若不存在默认取值abXpath, 该值是单次操作第一次获取的元素的abXpath, 用于扩大选区后再缩小选区找到初始元素路径上的元素， 仅在缩小选区时有用
      ...
   },
  "key": "getChildElement"
}

// 获取元素对象
{
  "browser_type": "chrome",
  "data": {
      "type": "xpath", // "xpath" | "cssSelector" | "text"
      "value": "//div",
      "returnType": "single" //  "single" | "list"
   },
  "key": "generateElement"
}
// 获取关联元素
{
    "key" : "getRelativeElement",
    "browser_type": "chrome",
    "data": {
           "matchTypes": [],
           "checkType": "visualization",
           "xpath": "",
           ...,
           "relativeOptions": {
              "relativeType": "child" | "parent" | "sibling",
              "elementGetType": "index" | "xpath" | "last" | "all" | "next" | "prev",
              "index": 1,
              "xpath": ""
           }
     }
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
- 插件通信依靠注册的token,token 会编码，例如Chrome 浏览器 token=$chrome$

## 7. 常见问题解答

- 部分基于Chromium开发的浏览器会自动加载 Chrome 浏览器的插件，若加载了本插件，但存在 token 与浏览器不匹配，也无法使用

## 8. 附录

- **错误码列表**：
```
  SUCCESS = '0000', // 成功
  UNKNOWN_ERROR = '5001', // 未知异常
  ELEMENT_NOT_FOUND = '5002', // 元素未找到
  EXECUTE_ERROR = '5003', // 执行错误
  VERSION_ERROR = '5004', // 版本错误
```
