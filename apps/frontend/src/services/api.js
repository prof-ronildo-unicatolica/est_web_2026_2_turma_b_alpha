const API_URL = 'http://localhost:8000'

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('access_token')

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const resposta = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers
  })

  if (resposta.status === 401) {
    localStorage.removeItem('access_token')
    return null
  }

  return resposta
}