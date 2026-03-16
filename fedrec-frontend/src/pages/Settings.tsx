import React, { useState, useEffect } from 'react'
import { Form, Input, Button, Card, message } from 'antd'
import { useAuth } from '@/store/auth'
import * as userApi from '@/api/user'

export default function Settings() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    form.setFieldsValue({
      institution: user?.institution,
      interests: user?.interests?.join('、'),
      researchDirections: user?.researchDirections?.join('、'),
    })
  }, [user, form])

  const onFinish = async (v: { institution?: string; interests?: string; researchDirections?: string }) => {
    setLoading(true)
    try {
      await userApi.updateProfile({
        institution: v.institution,
        interests: v.interests ? v.interests.split(/[、,，]/).map((s) => s.trim()).filter(Boolean) : undefined,
        researchDirections: v.researchDirections ? v.researchDirections.split(/[、,，]/).map((s) => s.trim()).filter(Boolean) : undefined,
      })
      message.success('保存成功')
    } catch (e: unknown) {
      message.error((e as { response?: { data?: { message?: string } } })?.response?.data?.message || '保存失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card title="个人画像管理">
      <p style={{ color: '#666', marginBottom: 16 }}>
        以下属性用于冷启动阶段属性视图的输入，数据仅以加密形式参与联邦训练，严格存储在本地。
      </p>
      <Form form={form} onFinish={onFinish} layout="vertical" style={{ maxWidth: 560 }}>
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
          <Button type="primary" htmlType="submit" loading={loading}>保存</Button>
        </Form.Item>
      </Form>
    </Card>
  )
}
