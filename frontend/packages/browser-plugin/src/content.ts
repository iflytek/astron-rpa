/** @format */
import { handle, moveListener } from './content/contentInject'

chrome.runtime.onMessage.addListener((message, _sender, senderResponse) => {
  const handleMessage = async () => {
    try {
      const result = await handle(message)
      return result
    }
    catch (error) {
      return { error: error.message }
    }
  }

  handleMessage().then(senderResponse)
  return true
})

window.addEventListener(
  'mousemove',
  (event: MouseEvent) => {
    moveListener(event, document, '')
  },
  true,
)
