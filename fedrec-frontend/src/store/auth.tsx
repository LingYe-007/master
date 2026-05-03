import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import type { User } from '@/types'
import * as authApi from '@/api/auth'
import * as userApi from '@/api/user'
import { mergeUserWithLocal, saveLocalProfile } from '@/utils/localProfile'

interface AuthContextValue {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  register: (data: { username: string; password: string; email?: string }) => Promise<void>
  refreshUser: () => Promise<void>
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
      const merged = mergeUserWithLocal(u)
      setUser(merged)
      localStorage.setItem('user', JSON.stringify(merged))
    } catch {
      const raw = localStorage.getItem('user')
      const base = raw ? (JSON.parse(raw) as User) : null
      setUser(base ? mergeUserWithLocal(base) : null)
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    if (token) {
      const stored = localStorage.getItem('user')
      if (stored) try { setUser(mergeUserWithLocal(JSON.parse(stored) as User)) } catch { /* ignore */ }
      loadUser()
    } else {
      setUser(null)
      setLoading(false)
    }
  }, [token, loadUser])

  const login = useCallback(async (username: string, password: string) => {
    const res = await authApi.login(username, password)
    let merged = mergeUserWithLocal(res.user)
    try {
      const raw = sessionStorage.getItem('fedrec_pending_profile')
      if (raw) {
        const p = JSON.parse(raw) as { username?: string; personalNo?: string; displayName?: string }
        if (p.username === username) {
          const patch: Partial<User> = {}
          if (p.personalNo) patch.personalNo = p.personalNo
          if (p.displayName) patch.displayName = p.displayName
          if (Object.keys(patch).length) {
            saveLocalProfile(merged.id, patch)
            merged = mergeUserWithLocal({ ...res.user, ...patch })
          }
          sessionStorage.removeItem('fedrec_pending_profile')
        }
      }
    } catch { /* ignore */ }
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(merged))
    setToken(res.token)
    setUser(merged)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }, [])

  const register = useCallback(async (data: { username: string; password: string; email?: string }) => {
    const res = await authApi.register(data)
    if (res.token && res.user) {
      const merged = mergeUserWithLocal(res.user)
      localStorage.setItem('token', res.token)
      localStorage.setItem('user', JSON.stringify(merged))
      setToken(res.token)
      setUser(merged)
    }
  }, [])

  const refreshUser = useCallback(async () => {
    if (!token) return
    try {
      const u = await userApi.getCurrentUser()
      const merged = mergeUserWithLocal(u)
      setUser(merged)
      localStorage.setItem('user', JSON.stringify(merged))
    } catch { /* ignore */ }
  }, [token])

  return (
    <AuthContext.Provider value={{ user, token, login, logout, register, refreshUser, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
