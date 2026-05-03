// 用户与认证
export interface User {
  id: string
  username: string
  email?: string
  isAdmin?: boolean
  /** 个人编号：联邦客户端侧展示/检索用，可与学号或自编号一致 */
  personalNo?: string
  /** 真实姓名（选填，用于画像展示） */
  displayName?: string
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
  /** 推荐所依据的元路径记号（如 U—P—A—P）；U 用户、P 论文、A 作者、V 场所、K 关键词、I 机构 */
  metaPaths?: string[]
  /** 通过上述元路径如何关联到该篇论文的自然语言说明（可解释推荐） */
  metaPathExplanation?: string
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
