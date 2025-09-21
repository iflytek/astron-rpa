import { useFormItemRequired } from '@/views/Arrange/components/atomForm/hooks/useFormItemSort'

export function requiredItem(itemData: RPA.Atom) {
  const texts = []
  const { inputList = [], outputList = [] } = itemData
  inputList.concat(outputList).forEach((item) => {
    if (useFormItemRequired(item)) {
      if (item.dynamics && !item?.show)
        return texts
      texts.push(`${item.title}必填`)
    }
  })
  return texts
}
