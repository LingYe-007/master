import { request } from '@/utils/request'
import type { TrainingState } from '@/types'
import { mockTrainingState } from './mock'

export function getTrainingState() {
  return request.get<TrainingState>('/admin/training').catch(() => mockTrainingState)
}
