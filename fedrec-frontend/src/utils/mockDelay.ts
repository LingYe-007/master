/** 模拟网络往返，避免无后端时推荐/监控「秒开」显得不真实 */
export function mockDelay(ms = 240): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
