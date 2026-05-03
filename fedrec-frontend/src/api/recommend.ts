import { request } from '@/utils/request'
import { mockDelay } from '@/utils/mockDelay'
import type { Paper } from '@/types'
import { mockPapers } from './mock'

export function getRecommendations() {
  return request
    .get<{ list: Paper[]; strategy: 'structure' | 'attribute' }>('/recommend')
    .catch(async () => {
      await mockDelay(280)
      return { list: mockPapers, strategy: 'structure' as const }
    })
}
