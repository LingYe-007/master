import { useState, useEffect, useCallback } from 'react'
import { Card, List, Tag, Spin, Typography, Button, Space, Row, Col, Empty } from 'antd'
import { ReloadOutlined, SettingOutlined } from '@ant-design/icons'
import { Link } from 'react-router-dom'
import * as recommendApi from '@/api/recommend'
import type { Paper } from '@/types'
import { useAuth } from '@/store/auth'
import { mergeUserWithLocal } from '@/utils/localProfile'

export default function Recommend() {
  const { user } = useAuth()
  const merged = user ? mergeUserWithLocal(user) : null
  const [loading, setLoading] = useState(true)
  const [list, setList] = useState<Paper[]>([])
  const [strategy, setStrategy] = useState<'structure' | 'attribute'>('structure')

  const load = useCallback(() => {
    setLoading(true)
    recommendApi
      .getRecommendations()
      .then((res: { list: Paper[]; strategy?: 'structure' | 'attribute' }) => {
        setList(res.list || [])
        setStrategy(res.strategy || 'structure')
      })
      .catch(() => setList([]))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }} wrap={false}>
        <Col flex="auto">
          <Space wrap>
            <Tag color={strategy === 'structure' ? 'blue' : 'green'} style={{ fontSize: 13, padding: '4px 10px' }}>
              {strategy === 'structure' ? '结构优先（有足够交互历史）' : '属性优先（冷启动 / 弱交互）'}
            </Tag>
            {merged?.personalNo && (
              <Typography.Text type="secondary">个人编号：{merged.personalNo}</Typography.Text>
            )}
          </Space>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={load} loading={loading}>
              刷新推荐
            </Button>
            <Link to="/settings">
              <Button type="primary" ghost icon={<SettingOutlined />}>
                填写个人信息与编号
              </Button>
            </Link>
          </Space>
        </Col>
      </Row>

      {!merged?.personalNo && (
        <Typography.Paragraph type="warning" style={{ marginBottom: 12 }}>
          建议先在「个人设置」中填写<strong>个人编号</strong>与研究兴趣等画像信息，以便与论文中的冷启动路由说明一致。
        </Typography.Paragraph>
      )}

      <Card title="学术资源推荐列表">
        {loading ? (
          <Spin size="large" style={{ display: 'block', margin: '48px auto' }} />
        ) : list.length === 0 ? (
          <Empty description="暂无推荐结果">
            <Link to="/settings">去完善个人设置</Link>
          </Empty>
        ) : (
          <List
            itemLayout="vertical"
            dataSource={list}
            locale={{ emptyText: '暂无数据' }}
            renderItem={(p, index) => {
              const hasMeta = (p.metaPaths?.length ?? 0) > 0 || p.metaPathExplanation
              const extraContent = hasMeta || p.recommendationReason
              return (
              <List.Item
                extra={
                  extraContent ? (
                    <div style={{ maxWidth: 300, textAlign: 'right' }}>
                      <Typography.Text strong style={{ fontSize: 12, display: 'block', marginBottom: 6 }}>
                        元路径说明
                      </Typography.Text>
                      {p.metaPaths?.length ? (
                        <div style={{ marginBottom: 8 }}>
                          {p.metaPaths.map((mp) => (
                            <Tag key={mp} color="geekblue" style={{ marginBottom: 4, fontFamily: 'ui-monospace, monospace' }}>
                              {mp}
                            </Tag>
                          ))}
                        </div>
                      ) : null}
                      <Typography.Paragraph
                        type="secondary"
                        style={{ fontSize: 12, marginBottom: 0, lineHeight: 1.55, textAlign: 'right' }}
                      >
                        {p.metaPathExplanation ||
                          (p.recommendationReason
                            ? `（未返回显式元路径）${p.recommendationReason}`
                            : '暂无元路径解释')}
                      </Typography.Paragraph>
                      <Typography.Text type="secondary" style={{ fontSize: 11, display: 'block', marginTop: 6 }}>
                        记号：U 用户 · P 论文 · A 作者 · V 场所 · K 关键词 · I 机构
                      </Typography.Text>
                    </div>
                  ) : null
                }
              >
                <List.Item.Meta
                  title={
                    <Space align="start">
                      <Typography.Text type="secondary" style={{ minWidth: 22 }}>{index + 1}.</Typography.Text>
                      <span>{p.title}</span>
                    </Space>
                  }
                  description={
                    <Space wrap size={[4, 4]}>
                      {p.authors?.length ? <span>{p.authors.join(', ')}</span> : null}
                      {p.venue ? <Tag>{p.venue}</Tag> : null}
                      {p.year ? <span>{p.year}</span> : null}
                    </Space>
                  }
                />
                {p.abstract && (
                  <Typography.Paragraph type="secondary" ellipsis={{ rows: 2, expandable: true }}>
                    {p.abstract}
                  </Typography.Paragraph>
                )}
              </List.Item>
              )
            }}
          />
        )}
      </Card>
    </div>
  )
}
