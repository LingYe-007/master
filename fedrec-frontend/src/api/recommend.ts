import { request } from '@/utils/request'
import type { Paper } from '@/types'
import { mockPapers } from './mock'

export function getRecommendations() {
  return request
    .get<{ list: Paper[]; strategy: 'structure' | 'attribute' }>('/recommend')
    .catch(() => ({ list: mockPapers, strategy: 'structure' as const }))
}
