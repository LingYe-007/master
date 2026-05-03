import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Dropdown } from 'antd'
import { FileTextOutlined, SettingOutlined, DashboardOutlined, LogoutOutlined } from '@ant-design/icons'
import { useAuth } from '@/store/auth'
import { mergeUserWithLocal } from '@/utils/localProfile'

const { Header, Content } = AntLayout

export function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const du = user ? mergeUserWithLocal(user) : null
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { key: '/', label: <Link to="/">学术推荐</Link>, icon: <FileTextOutlined /> },
    { key: '/settings', label: <Link to="/settings">个人设置</Link>, icon: <SettingOutlined /> },
    ...(user?.isAdmin ? [{ key: '/admin/monitor', label: <Link to="/admin/monitor">仿真监控</Link>, icon: <DashboardOutlined /> }] : []),
  ]

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <span style={{ color: '#fff', fontWeight: 600 }}>联邦论文推荐系统</span>
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            style={{ flex: 1, minWidth: 280 }}
          />
        </div>
        <Dropdown
          menu={{
            items: [
              { key: 'settings', icon: <SettingOutlined />, label: '个人设置', onClick: () => navigate('/settings') },
              { type: 'divider' },
              { key: 'logout', icon: <LogoutOutlined />, label: '退出', onClick: () => { logout(); navigate('/login') } },
            ],
          }}
        >
          <span style={{ color: '#fff', cursor: 'pointer' }}>
            {du?.username || '用户'}
            {du?.personalNo ? <span style={{ opacity: 0.85, marginLeft: 8 }}>（编号 {du.personalNo}）</span> : null}
          </span>
        </Dropdown>
      </Header>
      <Content style={{ padding: 24 }}>{children}</Content>
    </AntLayout>
  )
}
