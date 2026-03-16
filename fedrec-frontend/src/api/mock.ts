import type { Paper, TrainingState } from '@/types'

export const mockPapers: Paper[] = [
  {
    id: '1',
    title: 'Federated Graph Neural Networks for Recommendation',
    authors: ['Alice', 'Bob'],
    venue: 'WWW',
    year: 2024,
    abstract: 'We propose a federated learning framework for graph-based recommendation.',
    recommendationReason: '推荐该论文是因为与您的研究兴趣「联邦学习」高度相关。',
    strategy: 'structure',
  },
  {
    id: '2',
    title: 'Contrastive Learning on Heterogeneous Information Networks',
    authors: ['Carol', 'Dave'],
    venue: 'KDD',
    year: 2023,
    abstract: 'Contrastive learning for HIN representation.',
    recommendationReason: '推荐该学者是因为你们有共同的合作者。',
    strategy: 'attribute',
  },
]

// 模拟合理的联邦推荐训练曲线：Loss 随轮次下降并趋于稳定，Hit@5/NDCG@5 随轮次缓慢上升
function makeLossHistory(rounds: number): { round: number; value: number }[] {
  return Array.from({ length: rounds }, (_, i) => {
    const r = i + 1
    const decay = 1 - 0.65 * (1 - Math.exp(-r / 25))
    const noise = 0.02 * Math.sin(r * 0.5) + 0.01 * (r % 3)
    const value = Math.max(0.35, 1.25 * decay + noise)
    return { round: r, value: Math.round(value * 10000) / 10000 }
  })
}

function makeMetricHistory(rounds: number, start: number, end: number): { round: number; value: number }[] {
  return Array.from({ length: rounds }, (_, i) => {
    const r = i + 1
    const t = r / rounds
    const smooth = start + (end - start) * (1 - Math.exp(-t * 3))
    const noise = 0.005 * Math.sin(r * 0.4)
    const value = Math.min(1, Math.max(0, smooth + noise))
    return { round: r, value: Math.round(value * 10000) / 10000 }
  })
}

const ROUNDS = 62
const LOSS = makeLossHistory(ROUNDS)
const HIT5 = makeMetricHistory(ROUNDS, 0.048, 0.118)
const NDCG5 = makeMetricHistory(ROUNDS, 0.028, 0.072)

const LOG_MESSAGES = [
  'Server: 收到客户端 #3 梯度，当前轮次已收集 5/5',
  'GET /api/admin/training/metrics/history?page_size=100',
  'Aggregation: FedAvg 聚合完成，全局模型已更新',
  'Broadcast: 已向 5 个客户端下发全局参数',
  'Client #1 本地训练完成，Loss=0.412',
  'Client #2 本地训练完成，Loss=0.398',
  'GET /api/admin/training/status',
  'Server: 轮次 62 结束，下一轮等待客户端接入',
]

export const mockTrainingState: TrainingState = {
  currentRound: ROUNDS,
  totalRounds: 100,
  clientCount: 5,
  trainingStatus: 'stopped',
  trainingType: '分层联邦学习',
  auxServerCount: 5,
  clients: [
    { id: 'client_1', status: 'offline' },
    { id: 'client_2', status: 'online' },
    { id: 'client_3', status: 'online' },
    { id: 'client_4', status: 'online' },
    { id: 'client_5', status: 'offline' },
  ],
  lossHistory: LOSS,
  aucHistory: HIT5,
  hitHistory: HIT5,
  ndcgHistory: NDCG5,
  logEntries: Array.from({ length: 48 }, (_, i) => {
    const h = 9 + Math.floor(i / 6)
    const m = (i * 7) % 60
    const s = (i * 11) % 60
    const time = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
    return { time, level: 'INFO', message: LOG_MESSAGES[i % LOG_MESSAGES.length] }
  }),
}
