const ENV = import.meta.env

export const isDev = ENV.DEV
export const isProd = ENV.PROD

// 发布环境
export const isPublish = ENV.MODE === 'publish'

export const baseUrl = location.origin.includes('localhost') ? location.origin : `${location.origin}/client`
