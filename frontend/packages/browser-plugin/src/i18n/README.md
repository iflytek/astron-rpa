# Browser Plugin Internationalization (i18n)

## Overview

The browser plugin now supports internationalization with the following languages:
- **English** (en)
- **Chinese Simplified** (zh-CN)
- **Arabic** (ar)

## Architecture

The i18n implementation consists of:

1. **i18n Module** (`src/i18n/index.ts`) - Core i18n functionality
2. **Type Definitions** (`src/i18n/types.ts`) - TypeScript types for messages
3. **Language Files** - Translation files for each supported language:
   - `src/i18n/locales/en.ts` - English translations
   - `src/i18n/locales/zh-CN.ts` - Chinese (Simplified) translations
   - `src/i18n/locales/ar.ts` - Arabic translations

## Usage

### Basic Translation

Import the `t` function and use it to get translations:

```typescript
import { t } from '../i18n'

const message = t('errors.elementNotFound')
// Returns: "Element not found" (en) / "未找到元素" (zh-CN) / "لم يتم العثور على العنصر" (ar)
```

### Translation with Parameters

For dynamic content, use parameter interpolation:

```typescript
const message = t('errors.elementChangedAtNode', { 
  index: '5', 
  step: 'removed' 
})
// Returns: "Element changed at node 5 step removed"
```

### Setting Language

The language is automatically detected from:
1. Saved preference in `chrome.storage.local`
2. Browser language settings

To manually change the language:

```typescript
import { setLocale } from '../i18n'

await setLocale('en')     // Switch to English
await setLocale('zh-CN')  // Switch to Chinese
await setLocale('ar')     // Switch to Arabic
```

### Getting Current Language

```typescript
import { getLocale } from '../i18n'

const currentLocale = getLocale()
console.log(currentLocale) // 'en', 'zh-CN', or 'ar'
```

## Message Structure

All translations are organized into the following categories:

### Errors (`errors.*`)
- Background errors: Tab operations, element operations, execution errors
- Content errors: Element operations, validation errors

### Success Messages (`success.*`)
- Operation success messages

### HTML Tags (`tags.*`)
- Human-readable names for HTML tags (e.g., `div` → "Block Element")

### Input Types (`inputTypes.*`)
- Human-readable names for input types (e.g., `text` → "Text Input")

## Adding New Translations

### Step 1: Update Type Definition

Add the new key to `src/i18n/types.ts`:

```typescript
export interface Messages {
  errors: {
    // ... existing keys
    myNewError: string
  }
}
```

### Step 2: Add Translations

Update all language files with the translation:

**en.ts:**
```typescript
errors: {
  myNewError: 'My new error message',
}
```

**zh-CN.ts:**
```typescript
errors: {
  myNewError: '我的新错误信息',
}
```

**ar.ts:**
```typescript
errors: {
  myNewError: 'رسالة الخطأ الجديدة',
}
```

### Step 3: Use in Code

```typescript
import { t } from '../i18n'

const message = t('errors.myNewError')
```

## Implementation Details

### Getter Pattern

Constants and enums have been converted to use getter patterns to support dynamic language switching:

```typescript
// Before
export enum ErrorMessage {
  ELEMENT_NOT_FOUND = '未找到元素'
}

// After
export const ErrorMessage = {
  get ELEMENT_NOT_FOUND() { return t('errors.elementNotFound') }
}
```

This ensures that the correct translation is always returned, even if the language changes at runtime.

## Testing

To test different languages:

1. Open the browser extension
2. Open browser console
3. Change language programmatically:
   ```javascript
   chrome.storage.local.set({ locale: 'en' })
   chrome.storage.local.set({ locale: 'zh-CN' })
   chrome.storage.local.set({ locale: 'ar' })
   ```
4. Reload the extension

## RTL Support (Arabic)

For Arabic language support, additional CSS might be needed to properly handle right-to-left (RTL) text direction. Consider adding:

```css
[data-locale="ar"] {
  direction: rtl;
}
```

## Best Practices

1. **Never hardcode user-facing strings** - Always use the `t()` function
2. **Use descriptive keys** - Make translation keys clear and hierarchical
3. **Keep translations consistent** - Use similar terminology across messages
4. **Test all languages** - Verify translations work in all supported languages
5. **Consider text expansion** - Some languages (like German or Arabic) may use more space

## Future Enhancements

Potential improvements:
- Add more languages
- Implement date/time formatting per locale
- Add number formatting per locale
- Support for pluralization rules
- Language selector UI component
