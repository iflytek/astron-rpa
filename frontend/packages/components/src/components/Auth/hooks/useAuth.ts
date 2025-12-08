import { ref } from 'vue'

import type { AuthResponse, LoginFormData, RegisterFormData } from '../interface'

export function useAuth() {
  const loading = ref(false)
  const user = ref<AuthResponse['user'] | null>(null)

  const login = async (data: LoginFormData): Promise<AuthResponse> => {
    loading.value = true
    try {
      // 这里调用您的 API
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      if (!response.ok)
        throw new Error('Login failed')

      const result: AuthResponse = await response.json()
      user.value = result.user

      // 存储 token
      localStorage.setItem('token', result.token)

      return result
    }
    finally {
      loading.value = false
    }
  }

  const register = async (data: RegisterFormData): Promise<AuthResponse> => {
    loading.value = true
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      if (!response.ok)
        throw new Error('Registration failed')

      const result: AuthResponse = await response.json()
      user.value = result.user

      localStorage.setItem('token', result.token)

      return result
    }
    finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    loading,
    user,
    login,
    register,
    logout,
  }
}
