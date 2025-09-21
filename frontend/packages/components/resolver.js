const packageName = '@rpa/components'

export function RpaResolver() {
  return {
    type: 'component',
    resolve: (name) => {
      if (['RpaIcon', 'RpaHintIcon'].includes(name)) {
        const partialName = name.slice(3)
        return { name: partialName, from: packageName }
      }
    },
  }
}
