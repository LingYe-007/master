import { request } from '@/utils/request'
import type { User } from '@/types'

export function login(username: string, password: string) {
  return request.post<{ token: string; user: User }>('/auth/login', { username, password })
}

export function register(data: { username: string; password: string; email?: string }) {
  return request.post<{ token?: string; user: User }>('/auth/register', data)
}
