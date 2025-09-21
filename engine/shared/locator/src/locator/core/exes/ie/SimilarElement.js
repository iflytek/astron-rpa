function ElementInfo(xpath, abXpath, cssSelector, abCssSelector, pathDirs, parentClass, rect, domain, url, shadowRoot, tabTitle, tabUrl, favIconUrl, isFrame) {
  this.xpath = typeof xpath !== 'undefined' ? xpath : '';
  this.abXpath = typeof abXpath !== 'undefined' ? abXpath : '';
  this.cssSelector = typeof cssSelector !== 'undefined' ? cssSelector : '';
  this.abCssSelector = typeof abCssSelector !== 'undefined' ? abCssSelector : '';
  this.pathDirs = typeof  pathDirs !== 'undefined' ? pathDirs : [];
  this.parentClass = typeof parentClass !== 'undefined' ? parentClass : '';
  this.rect = typeof rect !== 'undefined' ? rect : { left: 0, top: 0, width: 0, height: 0, right: 0, bottom: 0, x: 0, y: 0 };
  this.domain = typeof domain !== 'undefined' ? domain : '';
  this.url = typeof url !== 'undefined' ? url : '';
  this.shadowRoot = typeof shadowRoot !== 'undefined' ? shadowRoot : false;
  this.tabTitle = typeof tabTitle !== 'undefined' ? tabTitle : '';
  this.tabUrl = typeof tabUrl !== 'undefined' ? tabUrl : '';
  this.favIconUrl = typeof favIconUrl !== 'undefined' ? favIconUrl : '';
  this.isFrame = typeof isFrame !== 'undefined' ? isFrame : false;
}

function generate_css_selector(elements) {
  /**
   * 将元素列表转换为符合W3C Selectors Level 3标准的CSS选择器字符串，支持索引选择
   */
  var selector_parts = [];
  var text_filters = [];

  for (var i = 0; i < elements.length; i++) {
      var element = elements[i];

      // 只处理checked为True的元素
      if (!element.checked) {
          continue;
      }

      // 添加标签名
      var part = element.tag;
      var has_index = false;
      var index_value = null;

      // 处理属性
      var attrs = element.attrs || [];
      for (var j = 0; j < attrs.length; j++) {
          var attr = attrs[j];

          // 先检查是否有@index属性并且checked为True
          if (attr.name === '@index' && attr.checked) {
              has_index = true;
              index_value = attr.value;
              continue;
          }

          // 处理其他checked为True的属性
          if (!attr.checked || (attr.name.indexOf('@') === 0 && attr.name !== '@index')) {
              continue;
          }

          var attr_name = attr.name;
          var attr_value = attr.value;

          // 处理不同类型的属性
          if (attr_name === 'class') {
              // 对于class属性，处理多个类名
              var classes = attr_value.split(' ');
              for (var k = 0; k < classes.length; k++) {
                  if (classes[k]) {
                      part += '.' + classes[k];
                  }
              }
          } else if (attr_name === 'id' && !isNumeric(attr_value)) {
              part += '#' + attr_value;
          } else if (attr_name === 'innerText') {
              // innerText不是标准CSS选择器的一部分，保存为文本过滤器
              text_filters.push({
                  element_index: selector_parts.length,
                  text: attr_value
              });
          } else {
              // 处理其他属性 - 使用精确匹配
              // 对引号进行转义
              var escaped_value = attr_value.replace(/'/g, "\\'");
              part += "[" + attr_name + "='" + escaped_value + "']";
          }
      }

      // 如果有索引属性，添加:nth-child()伪类
      if (has_index && index_value !== null && !(element.tag === 'html' && i === 0)) {
          part += ":nth-child(" + index_value + ")";
      }

      selector_parts.push(part);
  }

  // 使用 > 连接所有部分（符合要求的子选择器）
  return selector_parts.join(' > ');
}

// 辅助函数：检查字符串是否为数字
function isNumeric(str) {
  if (typeof str === 'number') return true;
  if (typeof str !== 'string') return false;
  return !isNaN(str) && !isNaN(parseFloat(str));
}

function getSimilarElement(preElementInfo, currentElementInfo) {
  if (!isSimilarElement(preElementInfo, currentElementInfo)) {
    return false;
  }
  var xpath = generateSimilarXapth(preElementInfo.xpath, currentElementInfo.xpath);
  //var cssSelector = generateSimilarSelector(preElementInfo.cssSelector, currentElementInfo.cssSelector);
  // 处理 pathDirs
  var pathDirs = generateSimilarPathDirs(preElementInfo.pathDirs, currentElementInfo.pathDirs);
  var cssSelector = generate_css_selector(pathDirs)
  var similarCount = document.querySelectorAll(cssSelector.split('>>')[0]).length;
  console.log(similarCount);


  // 手动合并对象的属性
  var similarElementInfo = {
    xpath: xpath,
    cssSelector: cssSelector,
    abXpath: preElementInfo.abXpath,
    abCssSelector: preElementInfo.abCssSelector,
    pathDirs: pathDirs,
    parentClass: preElementInfo.parentClass,
    rect: preElementInfo.rect,
    domain: preElementInfo.domain,
    url: preElementInfo.url,
    shadowRoot: preElementInfo.shadowRoot,
    tabTitle: preElementInfo.tabTitle,
    tabUrl: preElementInfo.tabUrl,
    favIconUrl: preElementInfo.favIconUrl,
    isFrame: preElementInfo.isFrame,
    iframeIndex: preElementInfo.iframeIndex,
    similarCount: similarCount
  };

  return similarElementInfo;
}

/**
 * 判断两个元素是否相似
 * @param {ElementInfo} preElementInfo
 * @param {ElementInfo} currentElementInfo
 * @returns
 */
function isSimilarElement(preElementInfo, currentElementInfo) {
  var xpath = preElementInfo.xpath;
  var cssSelector = preElementInfo.cssSelector;
  var pathDirs  = preElementInfo.pathDirs;

  var currentPathDirs = currentElementInfo.pathDirs;
  var currentXpath = currentElementInfo.xpath;
  var currentCssSelector = currentElementInfo.cssSelector;

  var xpathArr = xpath.split('/');
  var currentXpathArr = currentXpath.split('/');
  var cssSelectorArr = cssSelector.split('>');
  var currentCssSelectorArr = currentCssSelector.split('>');

  // 存在以下情况，则认为两个元素不是相似元素
  if (preElementInfo.url !== currentElementInfo.url) {
    return false;
  }
  if (xpathArr.length !== currentXpathArr.length) {
    return false;
  }

  // 若存在 tag 不一样，但是路径长度一样，则认为两个元素不是相似元素
  if (xpathArr.length === currentXpathArr.length) {
    for (var i = 0; i < xpathArr.length; i++) {
      var leftCharIndex = xpathArr[i].indexOf('[');
      var rightCharIndex = currentXpathArr[i].indexOf('[');
      var leftTag = xpathArr[i].substring(0, leftCharIndex);
      var rightTag = currentXpathArr[i].substring(0, rightCharIndex);
      if (leftTag !== rightTag) {
        return false;
      }
    }
  }

  if (cssSelectorArr.length !== currentCssSelectorArr.length) {
    return false;
  }

    // pathDirs 长度不一样，则认为两个元素不是相似元素
  if (pathDirs.length !== currentPathDirs.length) {
    return false;
  }

    // pathDirs 长度不一样，则认为两个元素不是相似元素
  if (pathDirs.length !== currentPathDirs.length) {
    return false;
  }
  return true;
}

/**
 * 得到相似的xpath，这里不在校验是否是相似元素
 * @param {string} preXpath
 * @param {string} currentXpath
 * @returns {string}
 */
function generateSimilarXapth(preXpath, currentXpath) {
  if (preXpath === currentXpath) {
    return preXpath;
  }
  var preXpathArr = preXpath.split('/');
  var currentXpathArr = currentXpath.split('/');
  for (let i = 0; i < preXpathArr.length; i++) {
    if (preXpathArr[i] !== currentXpathArr[i]) {
      // 不同 则去掉[*]
      // 去掉字符串tag[*]  中的[*]
      const reg = /\[(\d+)\]/;
      const match = preXpathArr[i].match(reg);
      if (match) {
        preXpathArr[i] = preXpathArr[i].replace(match[0], '');
      }
    }
  }
  let xpath = preXpathArr.join('/');
  return xpath;
}

/**
 * 得到相似的selector，这里不在校验是否是相似元素
 * @param {string} preSelector
 * @param {string} currentSelector
 * @returns {string}
 */
function generateSimilarSelector(preSelector, currentSelector) {
  if (preSelector === currentSelector) {
    return preSelector;
  }
  var preSelectorArr = preSelector.split('>');
  var currentSelectorArr = currentSelector.split('>');
  for (var i = 0; i < preSelectorArr.length; i++) {
    // nth-child
    if (preSelectorArr[i] !== currentSelectorArr[i] && preSelectorArr[i].indexOf(':nth-child') > -1) {
      preSelectorArr[i] = preSelectorArr[i].split(':nth-child')[0];
    }
    // class
    if (preSelectorArr[i] !== currentSelectorArr[i] && preSelectorArr[i].indexOf('.') > -1) {
      preSelectorArr[i] = preSelectorArr[i].split('.')[0];
    }
    // id #
    if (preSelectorArr[i] !== currentSelectorArr[i] && preSelectorArr[i].indexOf('#') > -1) {
      preSelectorArr[i] = preSelectorArr[i].split('#')[0];
    }
  }
  var selector = preSelectorArr.join('>');
  return selector;
}


function findItem(array, predicate) {
  for (var i = 0; i < array.length; i++) {
    if (predicate(array[i], i, array)) {
      return array[i];
    }
  }
  return undefined;
}

// 辅助函数：检查数组中是否存在满足条件的元素
function someItem(array, predicate) {
  for (var i = 0; i < array.length; i++) {
    if (predicate(array[i], i, array)) {
      return true;
    }
  }
  return false;
}

function generateSimilarPathDirs(prePathDirs, currentPathDirs) {
  // 逆向遍历 prePathDirs
  for (var i = prePathDirs.length - 1; i >= 0; i--) {
    var prePathDir = prePathDirs[i];
    var currentPathDir = currentPathDirs[i];

    // 遍历prePathDir的所有属性
    for (var j = 0; j < prePathDir.attrs.length; j++) {
      var attr = prePathDir.attrs[j];

      // 首先设置checked为false
      attr.checked = false;

      // 查找currentPathDir中对应名称的属性
      var currentAttr = findItem(currentPathDir.attrs, function(item) {
        return item.name === attr.name;
      });

      // 如果没有找到对应属性，清空值
      if (!currentAttr) {
        attr.value = '';
      }

      // 如果找到对应属性且是id类型，值相等且不为空，则设置为选中
      if (currentAttr && currentAttr.name === 'id' && attr.value === currentAttr.value && attr.value !== '') {
        attr.checked = true;
      }

      // 如果找到对应属性且是index类型，值相等且不为空，则设置为选中
      if (currentAttr && currentAttr.name === '@index' && attr.value !== '' && String(attr.value) === String(currentAttr.value)) {
        attr.checked = true;
      }

      // 如果找到对应属性且是innertext类型，设置为未选中并清空值
      if (currentAttr && currentAttr.name === 'innertext') {
        attr.checked = false;
        attr.value = '';
      }
    }

    // 检查是否存在已选中的id属性
    var idChecked = someItem(prePathDir.attrs, function(item) {
      return item.name === 'id' && item.checked;
    });

    // 如果存在已选中的id属性，则将其他所有属性设置为未选中
    if (idChecked) {
      for (var k = 0; k < prePathDir.attrs.length; k++) {
        var attr = prePathDir.attrs[k];
        if (attr.name !== 'id') {
          attr.checked = false;
        }
      }
    }
  }

  return prePathDirs;
}



// // 示例参数
// var elementInfoData = {
//   xpath: "/html/body/div[2]/div[1]/div[3]/div[2]/div[3]",
//   abXpath: "/html/body/div[2]/div[1]/div[3]/div[2]/div[3]",
//   cssSelector: "#Main > div:nth-child(2) > div:nth-child(3)",
//   abCssSelector: "#Main > div:nth-child(2) > div:nth-child(3)",
//   parentClass: "",
//   domain: "https://www.v2ex.com/",
//   url: "https://www.v2ex.com/",
//   shadowRoot: false,
//   tabTitle: "Document",
//   tabUrl: "https://www.v2ex.com/",
//   favIconUrl: "",  // 如果没有 favIconUrl，也可以传空字符串或其他默认值
//   isFrame: true
// };
// var elementInfoData2 = {
//   xpath: "/html/body/div[2]/div[1]/div[3]/div[2]/div[4]",
//   abXpath: "/html/body/div[2]/div[1]/div[3]/div[2]/div[4]",
//   cssSelector: "#Main > div:nth-child(2) > div:nth-child(4)",
//   abCssSelector: "#Main > div:nth-child(2) > div:nth-child(4)",
//   parentClass: "",
//   domain: "https://www.v2ex.com/",
//   url: "https://www.v2ex.com/",
//   shadowRoot: false,
//   tabTitle: "Document",
//   tabUrl: "https://www.v2ex.com/",
//   favIconUrl: "",  // 如果没有 favIconUrl，也可以传空字符串或其他默认值
//   isFrame: true
// };
//

//
// console.log(getSimilarElement(elementInfo,elementInfo2))
// {"xpath":"/html/body/div[2]/div[1]/div[3]/div[2]/div","cssSelector":"#Main > div:nth-child(2) > div","abXpath":"/html/body/div[2]/div[1]/div[3]/div[2]/div[3]","abCssSelector":"#Main > div:nth-child(2) > div:nth-child(3)","parentClass":"","rect":null,"domain":"https://www.v2ex.com/","url":"https://www.v2ex.com/","shadowRoot":false,"tabTitle":"Document","tabUrl":"https://www.v2ex.com/","favIconUrl":"","isFrame":true}