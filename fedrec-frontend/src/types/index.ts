// 用户与认证
export interface User {
  id: string
  username: string
  email?: string
  isAdmin?: boolean
  interests?: string[]
  institution?: string
  researchDirections?: string[]
}

// 推荐论文
export interface Paper {
  id: string
  title: string
  authors: string[]
  venue?: string
  year?: number
  abstract?: string
  keywords?: string[]
  recommendationReason?: string
  strategy?: 'structure' | 'attribute'
}

// 训练监控
export interface TrainingState {
  currentRound: number
  totalRounds?: number
  clientCount: number
  clients: { id: string; status: 'online' | 'offline' | 'training' }[]
  lossHistory: { round: number; value: number }[]
  aucHistory?: { round: number; value: number }[]
  hitHistory?: { round: number; value: number }[]
  ndcgHistory?: { round: number; value: number }[]
  trainingStatus?: 'running' | 'stopped'
  trainingType?: string
  auxServerCount?: number
  logEntries?: { time: string; level: string; message: string }[]
}
