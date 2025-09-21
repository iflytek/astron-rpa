import type { RuleObject } from 'ant-design-vue/es/form'
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

import { mirrorList } from '../config'

export function useInstallPython() {
  const { t } = useTranslation()
  const pacakgeOption = ref({
    packageName: '',
    packageVersion: '',
    mirror: mirrorList[0].value,
    output: '',
  })

  const rules: Record<string, RuleObject[]> = {
    packageName: [{ required: true, message: t('enterPackageName'), trigger: 'blur' }],
    mirror: [{ required: true, message: t('selectMirror'), trigger: 'change' }],
  }

  const pacakgeConfig = ref<Array<any>>([
    { key: 'packageName', label: t('packageName'), type: 'input', placeholder: t('enterPackageName') },
    { key: 'packageVersion', label: t('packageVersion'), type: 'input', placeholder: t('installLatestVersion') },
    { key: 'mirror', label: t('mirror'), type: 'select', placeholder: t('selectMirror'), options: mirrorList },
    { key: 'output', label: t('output'), type: 'textarea', placeholder: t('packageOutputMessage') },
  ])

  return {
    pacakgeOption,
    pacakgeConfig,
    rules,
  }
}
