import axios from "axios"
import type { InternalAxiosRequestConfig } from "axios"

// The refresh token lives in an HttpOnly cookie the browser sends for us. The access
// token is kept in memory only — localStorage would expose it to any script on the page.
let accessToken: string | null = null

export function setAccessToken(token: string | null) {
  accessToken = token
}

export function getAccessToken() {
  return accessToken
}

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "/api"

const apiClient = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // send the refresh_token cookie
})

apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

// Endpoints that answer 401 for their own reasons — a refresh here would mask the real error.
const AUTH_PATHS = ["/auth/login/", "/auth/register/", "/auth/token/refresh/"]

let refreshRequest: Promise<string> | null = null

function refreshAccessToken(): Promise<string> {
  // bare axios, so a 401 from the refresh itself can't re-enter this interceptor
  return axios
    .post<{ access: string }>(`${baseURL}/auth/token/refresh/`, {}, { withCredentials: true })
    .then(({ data }) => {
      setAccessToken(data.access)
      return data.access
    })
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config as (InternalAxiosRequestConfig & { retried?: boolean }) | undefined

    const shouldRefresh =
      error.response?.status === 401 &&
      original &&
      !original.retried &&
      !AUTH_PATHS.some((path) => original.url?.includes(path))

    if (!shouldRefresh) {
      return Promise.reject(error)
    }

    original.retried = true

    try {
      // share one refresh across every request that got a 401 at the same time
      refreshRequest ??= refreshAccessToken().finally(() => {
        refreshRequest = null
      })
      const token = await refreshRequest

      original.headers.Authorization = `Bearer ${token}`
      return apiClient(original)
    } catch (refreshError) {
      setAccessToken(null) // refresh cookie is gone or expired; the caller must log in again
      return Promise.reject(refreshError)
    }
  },
)

export default apiClient
