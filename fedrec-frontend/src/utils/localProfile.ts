import type { User } from '@/types'

/** 后端未实现的画像字段时，按用户 id 缓存在本地（与论文「本地私有库」演示一致） */
const key = (userId: string) => `fedrec_local_profile_${userId}`

export function loadLocalProfile(userId: string): Partial<User> {
  if (!userId) return {}
  try {
    const raw = localStorage.getItem(key(userId))
    if (!raw) return {}
    return JSON.parse(raw) as Partial<User>
  } catch {
    return {}
  }
}

export function saveLocalProfile(userId: string, patch: Partial<User>) {
  if (!userId) return
  const prev = loadLocalProfile(userId)
  localStorage.setItem(key(userId), JSON.stringify({ ...prev, ...patch }))
}

export function mergeUserWithLocal(user: User): User {
  const extra = loadLocalProfile(user.id)
  return { ...user, ...extra }
}
