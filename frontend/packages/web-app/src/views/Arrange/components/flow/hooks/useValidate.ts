import i18next from '@/plugins/i18next'

import { useFormItemRequired } from '@/views/Arrange/components/atomForm/hooks/useFormItemSort'

export function requiredItem(itemData: RPA.Atom) {
  const texts = []
  const { inputList = [], outputList = [] } = itemData
  inputList.concat(outputList).forEach((item) => {
    if (useFormItemRequired(item)) {
      if (item.dynamics && !item?.show)
        return texts
      texts.push(i18next.t('common.fieldIsRequired', { field: item.title }))
    }
  })
  return texts
}
