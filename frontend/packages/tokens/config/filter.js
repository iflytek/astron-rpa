export function isColor(token) {
  return (token?.$type || token?.type) === 'color'
}

export function isDark(token) {
  return token.dark !== undefined
}
