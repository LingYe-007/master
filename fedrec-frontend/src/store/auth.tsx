import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import type { User } from '@/types'
import * as authApi from '@/api/auth'
import * as userApi from '@/api/user'

interface AuthContextValue {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  register: (data: { username: string; password: string; email?: string }) => Promise<void>
  loading: boolean
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const u = await userApi.getCurrentUser()
      setUser(u as User)
    } catch {
      setUser(JSON.parse(localStorage.getItem('user') || 'null'))
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    if (token) {
      const stored = localStorage.getItem('user')
      if (stored) try { setUser(JSON.parse(stored)) } catch { /* ignore */ }
      loadUser()
    } else {
      setUser(null)
      setLoading(false)
    }
  }, [token, loadUser])

  const login = useCallback(async (username: string, password: string) => {
    const res = await authApi.login(username, password) as { token: string; user: User }
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.user))
    setToken(res.token)
    setUser(res.user)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }, [])

  const register = useCallback(async (data: { username: string; password: string; email?: string }) => {
    const res = await authApi.register(data) as { token?: string; user: User }
    if (res.token) {
      localStorage.setItem('token', res.token)
      localStorage.setItem('user', JSON.stringify(res.user))
      setToken(res.token)
      setUser(res.user)
    }
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, login, logout, register, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
