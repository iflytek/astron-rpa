import http from './http'

/**
 * AI合同要素抽取效果验证
 * @param data RPA.ConfigParamData
 */
export async function validateContractResult(data: string) {
  const res = await http.post('/scheduler/validate/contract', data)
  return res.data
}
