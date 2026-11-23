const API_URL = 'http://localhost:8000/api/v1'

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('access_token')

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const caminhoNormalizado = endpoint.startsWith('/api/v1')
    ? endpoint.replace(/^\/api\/v1/, '')
    : endpoint

  const resposta = await fetch(`${API_URL}${caminhoNormalizado}`, {
    ...options,
    headers
  })

  if (resposta.status === 401) {
    localStorage.removeItem('access_token')
    return null
  }

  return resposta
}
