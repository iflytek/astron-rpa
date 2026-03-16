/**
 * @file i18n module for browser plugin
 * Supports English, Chinese, and Arabic
 */

import { ar } from './locales/ar'
import { en } from './locales/en'
import { zhCN } from './locales/zh-CN'
import type { Locale, Messages } from './types'

const messages: Record<Locale, Messages> = {
  en,
  'zh-CN': zhCN,
  'ar': ar,
}

let currentLocale: Locale = 'zh-CN'

/**
 * Initialize i18n with locale from storage or browser settings
 */
export async function initI18n(): Promise<void> {
  try {
    const browserLang = navigator.language || 'zh-CN'
    if (browserLang.startsWith('zh')) {
      currentLocale = 'zh-CN'
    }
    else if (browserLang.startsWith('ar')) {
      currentLocale = 'ar'
    }
    else {
      currentLocale = 'en'
    }
  }
  catch (error) {
    console.error('Failed to initialize i18n:', error)
  }
}

/**
 * Get translation by key
 * @param key Translation key
 * @param params Optional parameters for string interpolation
 * @returns Translated string
 */
export function t(key: string, params?: Record<string, string | number>): string {
  const keys = key.split('.')
  let value: any = messages[currentLocale]

  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k]
    }
    else {
      console.warn(`Translation key not found: ${key}`)
      return key
    }
  }

  if (typeof value !== 'string') {
    console.warn(`Translation value is not a string: ${key}`)
    return key
  }

  // Simple parameter replacement
  if (params) {
    return value.replace(/\{(\w+)\}/g, (match, paramKey) => {
      return params[paramKey]?.toString() || match
    })
  }

  return value
}

/**
 * Set current locale
 * @param locale New locale
 */
export async function setLocale(locale: Locale): Promise<void> {
  if (messages[locale]) {
    currentLocale = locale
    await chrome.storage.local.set({ locale })
  }
  else {
    console.warn(`Unsupported locale: ${locale}`)
  }
}

/**
 * Get current locale
 * @returns Current locale
 */
export function getLocale(): Locale {
  return currentLocale
}

/**
 * Get all available locales
 * @returns Array of available locales
 */
export function getAvailableLocales(): Locale[] {
  return Object.keys(messages) as Locale[]
}

// Auto initialize
initI18n()
