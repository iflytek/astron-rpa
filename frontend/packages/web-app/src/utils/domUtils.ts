/**
 * 元素 name滚动到 视口
 * @param name 需要做 name 是否有效的前置拦截
 */
export function scrollToName(name: string, times?: number) {
  console.log('scrollToName: ', name)
  if (!name)
    return
  if (times <= 0) {
    return
  }
  else {
    times--
  }
  const element = document.getElementsByName(name)
  if (element && element[0]) {
    setTimeout(() => { // 防止滚动未成功，延迟300ms
      element[0].scrollIntoView({
        block: 'center',
      })
    }, 300)
  }
  else {
    const ti = setTimeout(() => {
      scrollToName(name, 10)
      clearTimeout(ti)
    }, 300)
  }
}
