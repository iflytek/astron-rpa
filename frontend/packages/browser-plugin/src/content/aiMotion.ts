import { Motion } from 'ai-motion'
import type { MotionOptions } from 'ai-motion'

export type { MotionOptions }

let motionInstance: Motion | null = null

function initAIMotion(options?: MotionOptions): Motion {
  const motion = new Motion({
    width: document.documentElement.clientWidth,
    height: document.documentElement.clientHeight,
    mode: 'light',
    ratio: devicePixelRatio,
    styles: {
      position: 'fixed',
      inset: '0',
      zIndex: '999999',
      pointerEvents: 'none',
    },
    colors: [
      'rgb(114, 111, 255)',
      'rgb(0, 242, 189)',
      'rgb(255, 172, 84)',
      'rgb(255, 79, 217)',
    ],
    ...options,
  })
  document.body.appendChild(motion.element)
  return motion
}

export async function startAIMotion(options?: MotionOptions) {
  if (!motionInstance) {
    motionInstance = initAIMotion(options)
  }
  motionInstance.start()
  await motionInstance.fadeIn()
  window.removeEventListener('resize', resizeAIMotion)
  window.addEventListener('resize', resizeAIMotion)
  return motionInstance
}

export async function stopAIMotion() {
  if (motionInstance) {
    motionInstance.pause()
    await motionInstance.fadeOut()
  }
}

export function destroyAIMotion() {
  if (motionInstance) {
    motionInstance.dispose()
    motionInstance = null
  }
}

export function getAIMotion() {
  return motionInstance
}

export function pauseAIMotion() {
  if (motionInstance) {
    motionInstance.pause()
  }
}

export function resumeAIMotion() {
  if (motionInstance) {
    motionInstance.start()
  }
}

function resizeAIMotion() {
  const width = document.documentElement.clientWidth
  const height = document.documentElement.clientHeight
  const ratio = devicePixelRatio
  if (motionInstance) {
    motionInstance.resize(width, height, ratio)
  }
}

export function focusElementAnimation(element: HTMLElement) {
  if (!element)
    return
  const rect = element.getBoundingClientRect()
  const dot = document.createElement('div')
  dot.className = 'rpa-ele-dotindicator'
  dot.style.left = `${rect.left + rect.width / 2 - 20}px`
  dot.style.top = `${rect.top + rect.height / 2 - 20}px`
  document.documentElement.appendChild(dot)
  setTimeout(() => {
    if (dot && dot.parentNode) {
      dot.parentNode.removeChild(dot)
    }
  }, 2000)
}

export function removeFocusElementAnimation() {
  const dots = document.querySelectorAll('.rpa-ele-dotindicator')
  dots.forEach(dot => {
    if (dot && dot.parentNode) {
      dot.parentNode.removeChild(dot)
    }
  })
}

export function highlightElementBorder(element: HTMLElement) {
  if (!element)
    return
  const oldOutline = element.style.outline
  element.style.outline = '2px solid #ff0000'
  setTimeout(() => {
    element.style.outline = oldOutline
  }, 1500);
}