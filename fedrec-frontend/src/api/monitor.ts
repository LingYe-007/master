import { request } from '@/utils/request'
import { mockDelay } from '@/utils/mockDelay'
import type { TrainingState } from '@/types'
import { mockTrainingState } from './mock'

export function getTrainingState() {
  return request.get<TrainingState>('/admin/training').catch(async () => {
    await mockDelay(320)
    return mockTrainingState
  })
}
