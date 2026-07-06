const rawBaseUrl = import.meta.env.VITE_API_URL?.trim() || '/api'

export const API_BASE_URL = `${rawBaseUrl.replace(/\/+$/, '')}/api`

export function apiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE_URL}${normalizedPath}`
}