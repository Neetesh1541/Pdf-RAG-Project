const API_BASE = ''

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers || {}),
    },
    ...options,
  })

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    const message = typeof data === 'object' && data?.detail ? data.detail : 'Request failed.'
    throw new Error(message)
  }

  return data
}

export const api = {
  getDocuments: () => request('/api/documents/'),
  uploadDocuments: (files) => {
    const formData = new FormData()
    Array.from(files).forEach((file) => formData.append('files', file))
    return request('/api/documents/upload/', { method: 'POST', body: formData })
  },
  deleteDocument: (id) => request(`/api/documents/${id}/`, { method: 'DELETE' }),
  searchDocuments: (query) => request(`/api/documents/search/?q=${encodeURIComponent(query)}`),
  getDashboard: () => request('/api/dashboard/'),
  getConversations: () => request('/api/conversations/'),
  getConversation: (id) => request(`/api/conversations/${id}/`),
  sendChat: (payload) => request('/api/chat/', { method: 'POST', body: JSON.stringify(payload) }),
  evaluate: (payload) => request('/api/evaluate/', { method: 'POST', body: JSON.stringify(payload) }),
}
