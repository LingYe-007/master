import React, { useState, useEffect, useRef } from 'react'
import { Card, Row, Col, Progress, InputNumber, Checkbox, Select, Button, Typography } from 'antd'
import * as echarts from 'echarts'
import * as monitorApi from '@/api/monitor'
import type { TrainingState } from '@/types'

const { Text } = Typography

function MetricChart({
  refEl,
  data,
  title,
  latest,
  max,
  min,
}: {
  refEl: React.RefObject<HTMLDivElement>
  data: { round: number; value: number }[]
  title: string
  latest: number
  max: number
  min: number
}) {
  useEffect(() => {
    if (!data?.length || !refEl.current) return
    const chart = echarts.init(refEl.current)
    chart.setOption({
      grid: { left: 40, right: 12, top: 24, bottom: 24 },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.map((d) => d.round), show: true },
      yAxis: { type: 'value', splitLine: { show: false } },
      series: [{ data: data.map((d) => d.value), type: 'line', smooth: true, symbol: 'none' }],
    })
    return () => chart.dispose()
  }, [data, refEl])

  return (
    <Card
      title={title}
      size="small"
      extra={
        <span style={{ fontSize: 12, color: '#666' }}>
          最新值 {latest.toFixed(4)} · 最大值 {max.toFixed(4)} · 最小值 {min.toFixed(4)}
        </span>
      }
    >
      <div ref={refEl} style={{ height: 180 }} />
    </Card>
  )
}

export default function Monitor() {
  const [state, setState] = useState<TrainingState | null>(null)
  const [hierarchical, setHierarchical] = useState(true)
  const [auxServers, setAuxServers] = useState(5)
  const [totalRounds, setTotalRounds] = useState(100)
  const [localEpochs, setLocalEpochs] = useState(1)
  const [batchSize, setBatchSize] = useState(32)
  const [lr, setLr] = useState(0.01)
  const [device, setDevice] = useState('cuda:0')
  const [clientsPerRegion, setClientsPerRegion] = useState(10)

  const lossRef = useRef<HTMLDivElement>(null)
  const hitRef = useRef<HTMLDivElement>(null)
  const ndcgRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetch = () => {
      monitorApi
        .getTrainingState()
        .then((data) => setState(data as TrainingState))
        .catch(() => setState(null))
    }
    fetch()
    const t = setInterval(fetch, 3000)
    return () => clearInterval(t)
  }, [])

  const status = state?.trainingStatus ?? 'stopped'
  const currentRound = state?.currentRound ?? 0
  const total = state?.totalRounds ?? 100
  const lossHistory = state?.lossHistory ?? []
  const hitHistory = state?.hitHistory ?? state?.aucHistory ?? []
  const ndcgHistory = state?.ndcgHistory ?? []
  const lossLatest = lossHistory.length ? lossHistory[lossHistory.length - 1].value : 0
  const lossMax = lossHistory.length ? Math.max(...lossHistory.map((d) => d.value)) : 0
  const lossMin = lossHistory.length ? Math.min(...lossHistory.map((d) => d.value)) : 0
  const hitLatest = hitHistory.length ? hitHistory[hitHistory.length - 1].value : 0
  const hitMax = hitHistory.length ? Math.max(...hitHistory.map((d) => d.value), 1) : 1
  const hitMin = hitHistory.length ? Math.min(...hitHistory.map((d) => d.value)) : 0
  const ndcgLatest = ndcgHistory.length ? ndcgHistory[ndcgHistory.length - 1].value : 0
  const ndcgMax = ndcgHistory.length ? Math.max(...ndcgHistory.map((d) => d.value), 1) : 1
  const ndcgMin = ndcgHistory.length ? Math.min(...ndcgHistory.map((d) => d.value)) : 0
  const logEntries = state?.logEntries ?? []

  return (
    <div style={{ maxWidth: 1200 }}>
      {/* 训练概览 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={24} align="middle">
          <Col>
            <Text strong>训练类型</Text>
            <div>{state?.trainingType ?? '分层联邦学习'}</div>
          </Col>
          <Col>
            <Text strong>训练状态</Text>
            <div style={{ color: status === 'stopped' ? '#ff4d4f' : '#52c41a' }}>
              {status === 'stopped' ? '已停止' : '运行中'}
            </div>
          </Col>
          <Col flex={1}>
            <Text strong>训练进度</Text>
            <Progress percent={total ? Math.round((currentRound / total) * 100) : 0} showInfo={false} />
            <div style={{ fontSize: 12, color: '#666' }}>
              {currentRound}/{total}
            </div>
          </Col>
        </Row>
      </Card>

      {/* 训练控制面板 */}
      <Card title="训练控制面板" size="small" style={{ marginBottom: 16 }}>
        <Checkbox checked={hierarchical} onChange={(e) => setHierarchical(e.target.checked)}>
          使用分层联邦学习架构
        </Checkbox>
        <Row gutter={16} style={{ marginTop: 16 }}>
          <Col>
            <Text type="secondary">副服务器数量:</Text>
            <InputNumber min={0} value={auxServers} onChange={(v) => setAuxServers(v ?? 0)} style={{ width: 72, marginLeft: 8 }} />
          </Col>
          <Col>
            <Text type="secondary">总训练轮数:</Text>
            <InputNumber min={1} value={totalRounds} onChange={(v) => setTotalRounds(v ?? 100)} style={{ width: 72, marginLeft: 8 }} />
          </Col>
          <Col>
            <Text type="secondary">本地训练轮次:</Text>
            <InputNumber min={1} value={localEpochs} onChange={(v) => setLocalEpochs(v ?? 1)} style={{ width: 72, marginLeft: 8 }} />
          </Col>
          <Col>
            <Text type="secondary">批次大小:</Text>
            <InputNumber min={1} value={batchSize} onChange={(v) => setBatchSize(v ?? 32)} style={{ width: 72, marginLeft: 8 }} />
          </Col>
          <Col>
            <Text type="secondary">学习率:</Text>
            <InputNumber step={0.001} value={lr} onChange={(v) => setLr(v ?? 0.01)} style={{ width: 72, marginLeft: 8 }} />
          </Col>
        </Row>
        <Row gutter={16} align="middle" style={{ marginTop: 12 }}>
          <Col>
            <Text type="secondary">设备:</Text>
            <Select
              value={device}
              onChange={setDevice}
              options={[
                { value: 'cuda:0', label: 'CUDA:0 (GPU)' },
                { value: 'cpu', label: 'CPU' },
              ]}
              style={{ width: 140, marginLeft: 8 }}
            />
          </Col>
          <Col>
            <Text type="secondary">每区域客户端:</Text>
            <InputNumber min={1} value={clientsPerRegion} onChange={(v) => setClientsPerRegion(v ?? 10)} style={{ width: 72, marginLeft: 8 }} />
          </Col>
          <Col>
            <Text type="secondary" style={{ fontSize: 12 }}>注意: 客户端数量由 ACM 集群自动决定</Text>
          </Col>
        </Row>
        <Button type="primary" style={{ marginTop: 16 }}>启动训练</Button>
      </Card>

      {/* 当前状态 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card size="small">
            <Text type="secondary">训练状态</Text>
            <div style={{ color: status === 'stopped' ? '#ff4d4f' : '#52c41a', fontWeight: 500 }}>
              {status === 'stopped' ? '已停止' : '运行中'}
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Text type="secondary">当前轮次</Text>
            <div>{currentRound}/{total}</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Text type="secondary">副服务器数量</Text>
            <div>{state?.auxServerCount ?? 0}</div>
          </Card>
        </Col>
      </Row>

      {/* 训练指标：Loss / Hit@5 / NDCG@5 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <MetricChart refEl={lossRef} data={lossHistory} title="训练损失 (Loss)" latest={lossLatest} max={lossMax} min={lossMin} />
        </Col>
        <Col span={8}>
          <MetricChart refEl={hitRef} data={hitHistory} title="Hit@5" latest={hitLatest} max={hitMax} min={hitMin} />
        </Col>
        <Col span={8}>
          <MetricChart refEl={ndcgRef} data={ndcgHistory} title="NDCG@5" latest={ndcgLatest} max={ndcgMax} min={ndcgMin} />
        </Col>
      </Row>

      {/* 训练日志 */}
      <Card
        title="训练日志"
        size="small"
        extra={<span style={{ fontSize: 12, color: '#666' }}>{logEntries.length}条</span>}
      >
        <div
          style={{
            height: 220,
            overflow: 'auto',
            fontFamily: 'monospace',
            fontSize: 12,
            background: '#fafafa',
            padding: 8,
            borderRadius: 4,
          }}
        >
          {logEntries.length === 0 ? (
            <Text type="secondary">暂无日志</Text>
          ) : (
            logEntries.map((entry, i) => (
              <div key={i} style={{ marginBottom: 4 }}>
                <span style={{ color: '#666' }}>{entry.time}</span> {entry.level} {entry.message}
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  )
}
