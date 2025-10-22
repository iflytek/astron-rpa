import http from './http'
import { getRootBaseURL } from './http/env'

/**
 * AI合同要素抽取效果验证
 * @param data RPA.ConfigParamData
 */
export function validateContractResult(data: string) {
  return http.post('/scheduler/validate/contract', data, { baseURL: getRootBaseURL() })
}
