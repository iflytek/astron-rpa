const { defineConfig } = require('@lobehub/i18n-cli');
const { env } = require('process');

const modelName = env.OPENAI_MODEL_NAME || 'azure/gpt-4o-mini';

module.exports = defineConfig({
  modelName,
  entry: 'locales/zh-CN.json',
  entryLocale: 'zh-CN',
  output: 'locales',
  outputLocales: ['en-US'],
  saveImmediately: true, // 每个翻译块完成后立即保存结果
  concurrency: 5,
  temperature: 0.3,
});
