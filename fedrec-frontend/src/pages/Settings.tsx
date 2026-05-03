import { useState, useEffect } from 'react'
import { Form, Input, Button, Card, message, Descriptions, Divider, Space, Typography } from 'antd'
import { Link } from 'react-router-dom'
import { useAuth } from '@/store/auth'
import * as userApi from '@/api/user'
import { mergeUserWithLocal, saveLocalProfile } from '@/utils/localProfile'
import type { User } from '@/types'

export default function Settings() {
  const { user, refreshUser } = useAuth()
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    if (!user) return
    const u = mergeUserWithLocal(user)
    form.setFieldsValue({
      personalNo: u.personalNo,
      displayName: u.displayName,
      institution: u.institution,
      interests: u.interests?.join('、'),
      researchDirections: u.researchDirections?.join('、'),
    })
  }, [user, form])

  const onFinish = async (v: {
    personalNo?: string
    displayName?: string
    institution?: string
    interests?: string
    researchDirections?: string
  }) => {
    if (!user) return
    setLoading(true)
    const splitList = (s?: string) =>
      s ? s.split(/[、,，]/).map((x) => x.trim()).filter(Boolean) : undefined
    const localPatch: Partial<User> = {
      personalNo: v.personalNo?.trim() || undefined,
      displayName: v.displayName?.trim() || undefined,
      institution: v.institution?.trim() || undefined,
      interests: splitList(v.interests),
      researchDirections: splitList(v.researchDirections),
    }
    saveLocalProfile(user.id, localPatch)
    try {
      await userApi.updateProfile({
        institution: localPatch.institution,
        interests: localPatch.interests,
        researchDirections: localPatch.researchDirections,
        personalNo: localPatch.personalNo,
        displayName: localPatch.displayName,
      })
    } catch {
      /* 后端若未实现新字段，仅依赖本地缓存 */
    }
    try {
      await refreshUser()
    } catch {
      const merged = mergeUserWithLocal({ ...user, ...localPatch })
      localStorage.setItem('user', JSON.stringify(merged))
    }
    message.success('保存成功（个人编号与姓名等与画像字段已写入本地；服务端若支持将同步）')
    setLoading(false)
  }

  if (!user) return null

  const merged = mergeUserWithLocal(user)

  return (
    <Space direction="vertical" size="large" style={{ width: '100%', maxWidth: 720 }}>
      <Card title="账户信息" size="small">
        <Descriptions column={1} size="small" bordered>
          <Descriptions.Item label="系统用户 ID">
            <Typography.Text code copyable>{merged.id}</Typography.Text>
          </Descriptions.Item>
          <Descriptions.Item label="登录用户名">{merged.username}</Descriptions.Item>
          <Descriptions.Item label="当前个人编号">
            {merged.personalNo || <Typography.Text type="secondary">未填写（请在下方表单填写）</Typography.Text>}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card
        title="个人画像与编号"
        extra={<Link to="/">返回推荐列表</Link>}
      >
        <Typography.Paragraph type="secondary" style={{ marginBottom: 16 }}>
          个人编号可用于实验管理与客户端标识；机构、兴趣与研究方向作为冷启动阶段属性视图输入。
          数据默认写入浏览器本地并与账户绑定，参与联邦训练时仍遵循「原始图与属性不出域」的设定。
        </Typography.Paragraph>
        <Form form={form} onFinish={onFinish} layout="vertical">
          <Form.Item
            name="personalNo"
            label="个人编号"
            rules={[{ max: 64, message: '不超过 64 字' }]}
            extra="可与学号、工号或实验用客户端编号一致；仅用于前端展示与本地缓存演示。"
          >
            <Input placeholder="例如：2023XXXX 或 client-01" allowClear />
          </Form.Item>
          <Form.Item name="displayName" label="姓名（选填）" rules={[{ max: 32, message: '不超过 32 字' }]}>
            <Input placeholder="真实姓名或昵称" allowClear />
          </Form.Item>
          <Divider plain orientation="left" style={{ margin: '8px 0 16px' }}>
            画像属性
          </Divider>
          <Form.Item name="institution" label="所属机构">
            <Input placeholder="如：西北大学" />
          </Form.Item>
          <Form.Item name="interests" label="研究兴趣">
            <Input.TextArea rows={2} placeholder="多个兴趣用顿号、或逗号分隔" />
          </Form.Item>
          <Form.Item name="researchDirections" label="研究方向">
            <Input.TextArea rows={2} placeholder="多个方向用顿号、或逗号分隔" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              保存
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </Space>
  )
}
