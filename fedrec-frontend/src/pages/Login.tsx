import { useState } from 'react'
import { Form, Input, Button, Card, message } from 'antd'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '@/store/auth'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const onFinish = async (v: { username: string; password: string }) => {
    setLoading(true)
    try {
      await login(v.username, v.password)
      message.success('登录成功')
      navigate('/')
    } catch (e: unknown) {
      // 无后端时使用演示账号：demo / demo（管理员）；user / user（普通用户）
      if (v.username === 'demo' && v.password === 'demo') {
        localStorage.setItem('token', 'mock-token-admin')
        localStorage.setItem(
          'user',
          JSON.stringify({
            id: 'srv-admin-fedascl-01',
            username: 'demo',
            email: 'fedascl.ops@nwu-lab.cn',
            isAdmin: true,
            personalNo: 'OP-2026-FL',
            displayName: '系统管理员（演示）',
            institution: '西北大学 · 联邦学习仿真平台',
            interests: ['联邦运维', '训练监控', '语义压缩'],
            researchDirections: ['分布式训练', '分层聚合'],
          }),
        )
        window.location.href = '/'
        return
      }
      if (v.username === 'user' && v.password === 'user') {
        localStorage.setItem('token', 'mock-token-user')
        localStorage.setItem(
          'user',
          JSON.stringify({
            id: 'client-user-9f3c21',
            username: 'user',
            email: 'grad.m.example@stumail.nwu.edu.cn',
            isAdmin: false,
            personalNo: 'M2023-3248',
            displayName: '李研',
            institution: '信息科学与技术学院',
            interests: ['图神经网络', '论文推荐', '非IID联邦'],
            researchDirections: ['异质信息网络', '对比学习'],
          }),
        )
        window.location.href = '/'
        return
      }
      message.error((e as { response?: { data?: { message?: string } } })?.response?.data?.message || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: '80px auto' }}>
      <Card title="登录" extra={<Link to="/register">注册</Link>}>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>登录</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
