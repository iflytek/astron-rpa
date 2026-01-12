export function toUnicode(str: string): string {
  return str.split('').map((char) => {
    const code = char.charCodeAt(0).toString(16).toUpperCase()
    return `\\u${'0000'.slice(0, 4 - code.length) + code}`
  }).join('')
}
