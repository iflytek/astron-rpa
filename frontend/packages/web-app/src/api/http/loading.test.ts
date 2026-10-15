import { describe, expect, it, vi } from 'vitest'

import {
  GlobalLoadingTracker,
  shouldTrackGlobalLoading,
} from './loadingTracker'

describe('GlobalLoadingTracker', () => {
  it('keeps loading open until every concurrent request finishes', () => {
    const open = vi.fn()
    const close = vi.fn()
    const tracker = new GlobalLoadingTracker(open, close)

    tracker.start()
    tracker.start()
    expect(open).toHaveBeenCalledTimes(1)

    tracker.finish()
    expect(close).not.toHaveBeenCalled()

    tracker.finish()
    expect(close).toHaveBeenCalledTimes(1)
  })

  it('ignores unmatched finishes', () => {
    const open = vi.fn()
    const close = vi.fn()
    const tracker = new GlobalLoadingTracker(open, close)

    tracker.finish()
    tracker.finish()

    expect(open).not.toHaveBeenCalled()
    expect(close).not.toHaveBeenCalled()
  })
})

describe('shouldTrackGlobalLoading', () => {
  it('tracks loading unless it is explicitly disabled', () => {
    expect(shouldTrackGlobalLoading()).toBe(true)
    expect(shouldTrackGlobalLoading(false)).toBe(false)
  })
})
