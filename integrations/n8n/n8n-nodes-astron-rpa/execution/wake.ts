/** Optional latency optimization. n8n's persisted waitTill remains authoritative
 * and recovers without this timer after a process restart (up to one scanner tick).
 * The callback carries no results, inputs or RPA credentials.
 */
export function scheduleWake(resumeUrl: string, at: number): void {
  const timer = setTimeout(
    () => {
      void fetch(resumeUrl, {
        method: "POST",
        redirect: "error",
        signal: AbortSignal.timeout(5000),
      }).catch(() => undefined);
    },
    Math.max(250, at - Date.now() + 100),
  );
  timer.unref();
}
