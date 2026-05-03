import { request } from '@/utils/request'
import type { User } from '@/types'

export function getCurrentUser() {
  return request.get<User>('/user/me')
}

export function updateProfile(data: {
  interests?: string[]
  institution?: string
  researchDirections?: string[]
  personalNo?: string
  displayName?: string
}) {
  return request.put<User>('/user/profile', data)
}
