import axios, { type AxiosInstance } from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

/** 响应拦截器已解包为 res.data，此处收窄类型便于各 API 直接使用 T */
type ApiRequest = Pick<AxiosInstance, 'interceptors' | 'defaults'> & {
  get<T>(url: string, config?: Parameters<AxiosInstance['get']>[1]): Promise<T>
  post<T>(url: string, data?: unknown, config?: Parameters<AxiosInstance['post']>[2]): Promise<T>
  put<T>(url: string, data?: unknown, config?: Parameters<AxiosInstance['put']>[2]): Promise<T>
}

const raw = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
}) as ApiRequest

raw.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

raw.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const request = raw
