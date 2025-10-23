import type { Rule } from 'ant-design-vue/es/form'
/**
 * 手机号格式验证
 */
async function phoneValidate(_rule: Rule, value: string) {
  if (!value) {
    return Promise.reject(new Error('手机号不能为空！'))
  }
  if (!/^\d{11}$/.test(value)) {
    return Promise.reject(new Error('请输入正确的手机号格式！'))
  }
  return Promise.resolve()
}

/**
 * 账户空格校验
 */
async function validateTrim(_rule: Rule, value: string) {
  const trimReg = /\s+/g // 匹配空格
  if (trimReg.test(value)) {
    return Promise.reject(new Error('请输入正确的密码'))
  }
  else {
    return Promise.resolve()
  }
}

/**
 * 账户校验
 */
async function validateAccount(_rule: Rule, value: string) {
  console.log('validateAccount: ', value)
  const accountReg = /\s+/g // 匹配空格
  if (!value) {
    return Promise.reject(new Error('账号不能为空'))
  }
  if (accountReg.test(value)) {
    return Promise.reject(new Error('请输入正确的账号'))
  }
  else {
    return Promise.resolve()
  }
}

/**
 * 密码校验
 */
async function validatePass(_rule: Rule, value: string) {
  const res = value.replace(/\s*/g, '')
  const passwordReg = /^[a-z0-9\x21-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]{6,20}$/i
  if (value === '') {
    return Promise.reject(new Error('密码不能为空'))
  }
  // 数量
  if (res.length < 6 || res.length > 20) {
    return Promise.reject(new Error('密码长度6-20位'))
  }
  if (!passwordReg.test(res)) {
    return Promise.reject(new Error('请输入正确的密码格式，包含英文，数字，英文符号'))
  }
  else {
    return Promise.resolve()
  }
}
/**
 * 新密码校验
 */
async function validatePassNew(_rule: Rule, value: string) {
  const res = value.replace(/\s*/g, '')
  const numReg = /\d/
  const AZReg = /[A-Z]/
  const azReg = /[a-z]/
  const spReg = /[!@#$%^&*()?]/
  if (res.length < 6 || res.length > 20) {
    return Promise.reject(new Error('密码长度6-20位'))
  }
  if (!numReg.test(res)) {
    return Promise.reject(new Error('密码至少包含数字'))
  }
  if (!AZReg.test(res)) {
    return Promise.reject(new Error('密码至少包含大写字母'))
  }
  if (!azReg.test(res)) {
    return Promise.reject(new Error('密码至少包含小写字母'))
  }
  if (!spReg.test(res)) {
    return Promise.reject(new Error('密码至少特殊字符!@#$%^&*()?'))
  }
  return Promise.resolve()
}
/**
 * 短信验证码格式验证
 */
async function codeValidate(_rule: Rule, value: string) {
  if (!/^\d{6}$/.test(value)) {
    return Promise.reject(new Error('请输入正确的6位验证码！'))
  }
  return Promise.resolve()
}

/**
 * 邮箱格式验证
 */
async function emailValidate(_rule: Rule, value: string) {
  if (!/^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(value)) {
    return Promise.reject(new Error('请输入正确的邮箱！'))
  }
  return Promise.resolve()
}

/**
 * url格式验证
 */
async function urlValidate(_rule: Rule, value: string) {
  const pattern = /^[a-z]+:\/\/[a-z0-9\-.]+\.[a-z]{2,}(\/\S*)?$/i
  if (!pattern.test(value)) {
    return Promise.reject(new Error('请输入正确的网址！'))
  }
  return Promise.resolve()
}

/**
 * 文件地址格式验证
 */
async function fileUrlValidate(_rule: Rule, value: string) {
  if (!/^[C-F|]:\\.+\\.+$/.test(value)) {
    return Promise.reject(new Error('请输入正确的程序地址！'))
  }
  return Promise.resolve()
}

/**
 * 邮箱校验xxx@xxx.xxx
 */
async function validateEmail(_rule: Rule, value: string) {
  const emailReg = /^[\w-]+@[\w-]+(\.[\w-]+)+$/
  // 163邮箱
  if (!emailReg.test(value)) {
    return Promise.reject(new Error('请输入正确的邮箱！'))
  }
  else {
    return Promise.resolve()
  }
}

export {
  codeValidate,
  emailValidate,
  fileUrlValidate,
  phoneValidate,
  urlValidate,
  validateAccount,
  validateEmail,
  validatePass,
  validatePassNew,
  validateTrim,
}
