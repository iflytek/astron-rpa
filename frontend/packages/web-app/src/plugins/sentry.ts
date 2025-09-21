import type { User } from '@sentry/vue'
import type { App } from 'vue'

import { isProd, isPublish } from '@/utils/env'

const sentryDsn = import.meta.env.VITE_SENTRY_DSN

class SentryPlugin {
  private sentryPromise: Promise<typeof import('@sentry/vue')> | null = null

  private getSentry() {
    if (!this.sentryPromise) {
      this.sentryPromise = import('@sentry/vue')
    }
    return this.sentryPromise
  }

  async install(app: App<Element>) {
    if (!sentryDsn) {
      return
    }

    const sentry = await this.getSentry()

    sentry.init({
      app,
      enabled: isProd,
      environment: isPublish ? 'production' : 'development',
      dsn: sentryDsn,
      integrations: [
        sentry.browserTracingIntegration(),
        sentry.replayIntegration(),
      ],
      // Tracing
      tracesSampleRate: 0, // 关闭分布式追踪
      // Session Replay
      replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
      replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
    })
  }

  async setUser(user: User) {
    if (!sentryDsn) {
      return
    }

    const sentry = await this.getSentry()
    sentry.setUser(user)
  }
}

export default new SentryPlugin()
