import React, { useState, useEffect } from 'react'
import { Card, List, Tag, Spin, Typography } from 'antd'
import * as recommendApi from '@/api/recommend'
import type { Paper } from '@/types'

export default function Recommend() {
  const [loading, setLoading] = useState(true)
  const [list, setList] = useState<Paper[]>([])
  const [strategy, setStrategy] = useState<'structure' | 'attribute'>('structure')

  useEffect(() => {
    recommendApi
      .getRecommendations()
      .then((res: { list: Paper[]; strategy?: 'structure' | 'attribute' }) => {
        setList(res.list || [])
        setStrategy(res.strategy || 'structure')
      })
      .catch(() => setList([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '48px auto' }} />

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Tag color={strategy === 'structure' ? 'blue' : 'green'}>
          {strategy === 'structure' ? '结构优先（基于交互图）' : '属性优先（冷启动）'}
        </Tag>
      </div>
      <Card title="学术资源推荐">
        {list.length === 0 ? (
          <Typography.Text type="secondary">暂无推荐，请先完善个人设置或等待训练完成。</Typography.Text>
        ) : (
          <List
            itemLayout="vertical"
            dataSource={list}
            renderItem={(p) => (
              <List.Item
                extra={p.recommendationReason && (
                  <span style={{ fontSize: 12, color: '#666' }}>{p.recommendationReason}</span>
                )}
              >
                <List.Item.Meta
                  title={p.title}
                  description={
                    <>
                      {p.authors?.length && <span>{p.authors.join(', ')}</span>}
                      {p.venue && <Tag style={{ marginLeft: 8 }}>{p.venue}</Tag>}
                      {p.year && <span style={{ marginLeft: 8 }}>{p.year}</span>}
                    </>
                  }
                />
                {p.abstract && <Typography.Paragraph ellipsis={{ rows: 2 }}>{p.abstract}</Typography.Paragraph>}
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  )
}
