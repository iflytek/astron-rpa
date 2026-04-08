import http from './http'

export interface MacPermissions {
  accessibility: boolean
  screen_recording: boolean
  full_disk_access: boolean
}

export function getMacPermissionStatus() {
  return http.get<{ data: MacPermissions }>('/scheduler/mac_permission/status')
}

export function openMacPermissionSettings(type: 'accessibility' | 'screen_recording' | 'full_disk_access') {
  return http.post('/scheduler/mac_permission/open', { type })
}
