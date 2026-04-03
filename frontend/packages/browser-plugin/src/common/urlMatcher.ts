/**
 * URL matcher levels
 */
export enum UrlMatchLevel {
  NO_MATCH = 0, // Not matched
  DOMAIN = 1, // Domain matched
  DOMAIN_PATH = 2, // Domain + path matched
  DOMAIN_PATH_QUERY = 3, // Domain + path + query matched
  EXACT = 4, // Exact match
}

/**
 * URL match result
 */
export interface UrlMatchResult {
  level: UrlMatchLevel
  score: number // Matching score from 0 to 100
  details: {
    domainMatch: boolean
    pathMatch: boolean
    queryMatch: boolean
    hashMatch: boolean
    protocolMatch: boolean
  }
}

/**
 * URL matcher
 */
export class UrlMatcher {
  /**
   * Match two URLs
   * @param url1 First URL
   * @param url2 Second URL
   * @returns Match result
   */
  static match(url1: string, url2: string): UrlMatchResult {
    try {
      const parsed1 = new URL(url1)
      const parsed2 = new URL(url2)

      const details = {
        protocolMatch: parsed1.protocol === parsed2.protocol,
        domainMatch: this.matchDomain(parsed1, parsed2),
        pathMatch: this.matchPath(parsed1.pathname, parsed2.pathname),
        queryMatch: this.matchQuery(parsed1.search, parsed2.search),
        hashMatch: parsed1.hash === parsed2.hash,
      }

      // Calculate match level
      const level = this.calculateLevel(details)

      // Calculate match score
      const score = this.calculateScore(details, parsed1, parsed2)

      return { level, score, details }
    }
    catch (error) {
      console.error('URL parsing error:', error)
      return {
        level: UrlMatchLevel.NO_MATCH,
        score: 0,
        details: {
          domainMatch: false,
          pathMatch: false,
          queryMatch: false,
          hashMatch: false,
          protocolMatch: false,
        },
      }
    }
  }

  /**
   * Match domain (supports subdomains)
   */
  private static matchDomain(url1: URL, url2: URL): boolean {
    const host1 = url1.hostname.toLowerCase()
    const host2 = url2.hostname.toLowerCase()

    // Exactly the same
    if (host1 === host2)
      return true

    // Compare after removing www
    const withoutWww1 = host1.replace(/^www\./, '')
    const withoutWww2 = host2.replace(/^www\./, '')
    if (withoutWww1 === withoutWww2)
      return true

    // Check if they are the same root domain
    const domain1 = this.getRootDomain(host1)
    const domain2 = this.getRootDomain(host2)
    return domain1 === domain2
  }

  /**
   * Get root domain
   */
  private static getRootDomain(hostname: string): string {
    const parts = hostname.split('.')
    // Handle second-level domains (e.g. .co.uk, .com.cn)
    if (parts.length >= 3) {
      const lastTwo = parts.slice(-2).join('.')
      if (['co.uk', 'com.cn', 'com.au', 'co.jp'].includes(lastTwo)) {
        return parts.slice(-3).join('.')
      }
    }
    // Return the last two parts as the root domain
    return parts.slice(-2).join('.')
  }

  /**
   * Match path
   */
  private static matchPath(path1: string, path2: string): boolean {
    const normalize = (p: string) => {
      p = p.toLowerCase()
      // Remove trailing slash
      if (p.endsWith('/') && p.length > 1) {
        p = p.slice(0, -1)
      }
      return p
    }

    const p1 = normalize(path1)
    const p2 = normalize(path2)

    // Exact match
    if (p1 === p2)
      return true

    // Partial path match (shorter path is prefix of longer path)
    if (p1.startsWith(p2) || p2.startsWith(p1)) {
      return true
    }

    return false
  }

  /**
   * Match query parameters
   */
  private static matchQuery(search1: string, search2: string): boolean {
    if (search1 === search2)
      return true
    if (!search1 && !search2)
      return true
    if (!search1 || !search2)
      return false

    const params1 = new URLSearchParams(search1)
    const params2 = new URLSearchParams(search2)

    // Same number of parameters and all parameters match
    if (params1.size !== params2.size)
      return false

    for (const [key, value] of params1) {
      if (params2.get(key) !== value) {
        return false
      }
    }

    return true
  }

  /**
   * Calculate match level
   */
  private static calculateLevel(details: UrlMatchResult['details']): UrlMatchLevel {
    if (!details.domainMatch) {
      return UrlMatchLevel.NO_MATCH
    }

    if (details.domainMatch && !details.pathMatch) {
      return UrlMatchLevel.DOMAIN
    }

    if (details.domainMatch && details.pathMatch && !details.queryMatch) {
      return UrlMatchLevel.DOMAIN_PATH
    }

    if (details.domainMatch && details.pathMatch && details.queryMatch && !details.hashMatch) {
      return UrlMatchLevel.DOMAIN_PATH_QUERY
    }

    if (details.domainMatch && details.pathMatch && details.queryMatch && details.hashMatch && details.protocolMatch) {
      return UrlMatchLevel.EXACT
    }

    return UrlMatchLevel.DOMAIN_PATH_QUERY
  }

  /**
   * Calculate match score (0-100)
   */
  private static calculateScore(
    details: UrlMatchResult['details'],
    url1: URL,
    url2: URL,
  ): number {
    let score = 0

    // Domain match: 30 points
    if (details.domainMatch) {
      score += 30
      // Extra points for exactly the same hostname
      if (url1.hostname === url2.hostname) {
        score += 10
      }
    }

    // Path match: 25 points
    if (details.pathMatch) {
      score += 25
      // Extra points for exactly the same path
      if (url1.pathname === url2.pathname) {
        score += 10
      }
    }

    // Query match: 15 points
    if (details.queryMatch) {
      score += 15
    }

    // Hash match: 10 points
    if (details.hashMatch) {
      score += 10
    }

    // Protocol match: 10 points
    if (details.protocolMatch) {
      score += 10
    }

    return Math.min(score, 100)
  }

  /**
   * Simplified match method: only returns whether matched and match level
   */
  static simpleMatch(url1: string, url2: string, minLevel: UrlMatchLevel = UrlMatchLevel.DOMAIN): boolean {
    const result = this.match(url1, url2)
    return result.level >= minLevel
  }

  /**
   * Find the best matched URL from a list
   */
  static findBestMatch(targetUrl: string, urlList: string[]): { url: string, result: UrlMatchResult } | null {
    let bestMatch: { url: string, result: UrlMatchResult } | null = null
    let highestScore = 0

    for (const url of urlList) {
      const result = this.match(targetUrl, url)
      if (result.score > highestScore) {
        highestScore = result.score
        bestMatch = { url, result }
      }
    }

    return bestMatch
  }
}

// Export convenient methods
export function matchUrl(url1: string, url2: string): UrlMatchResult {
  return UrlMatcher.match(url1, url2)
}

export function isUrlMatch(url1: string, url2: string, minLevel: UrlMatchLevel = UrlMatchLevel.DOMAIN): boolean {
  return UrlMatcher.simpleMatch(url1, url2, minLevel)
}
