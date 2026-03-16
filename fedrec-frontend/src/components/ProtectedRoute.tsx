import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/store/auth'
import { Spin } from 'antd'

export function ProtectedRoute({ children, adminOnly }: { children: React.ReactNode; adminOnly?: boolean }) {
  const { user, token, loading } = useAuth()
  const location = useLocation()

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '48px auto' }} />
  if (!token || !user) return <Navigate to="/login" state={{ from: location }} replace />
  if (adminOnly && !user.isAdmin) return <Navigate to="/" replace />

  return <>{children}</>
}
