import { useState } from 'react'
import { Form, Input, Button, Card, message, Typography } from 'antd'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '@/store/auth'

export default function Register() {
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const onFinish = async (v: {
    username: string
    password: string
    email?: string
    personalNo?: string
    displayName?: string
  }) => {
    setLoading(true)
    try {
      const { username, personalNo, displayName, password, email } = v
      if (personalNo?.trim() || displayName?.trim()) {
        sessionStorage.setItem(
          'fedrec_pending_profile',
          JSON.stringify({
            username,
            personalNo: personalNo?.trim() || undefined,
            displayName: displayName?.trim() || undefined,
          })
        )
      }
      await register({ username, password, email })
      message.success('注册成功，请登录')
      navigate('/login')
    } catch (e: unknown) {
      message.error((e as { response?: { data?: { message?: string } } })?.response?.data?.message || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 440, margin: '64px auto' }}>
      <Card title="注册" extra={<Link to="/login">去登录</Link>}>
        <Typography.Paragraph type="secondary" style={{ fontSize: 13 }}>
          可选填写个人编号与姓名，将在首次登录时自动合并到账户（本地缓存，与论文「个人画像」一致）。
        </Typography.Paragraph>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="email" label="邮箱">
            <Input type="email" />
          </Form.Item>
          <Form.Item name="personalNo" label="个人编号（选填）">
            <Input placeholder="学号、工号或实验客户端编号" />
          </Form.Item>
          <Form.Item name="displayName" label="姓名（选填）">
            <Input placeholder="姓名或昵称" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              注册
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
