export function shouldTrackGlobalLoading(loading?: boolean) {
  return loading !== false
}

export class GlobalLoadingTracker {
  private activeRequests = 0

  constructor(
    private readonly open: () => void,
    private readonly close: () => void,
  ) {}

  start() {
    if (this.activeRequests === 0) {
      this.open()
    }

    this.activeRequests += 1
  }

  finish() {
    if (this.activeRequests === 0) {
      return
    }

    this.activeRequests -= 1
    if (this.activeRequests === 0) {
      this.close()
    }
  }
}
