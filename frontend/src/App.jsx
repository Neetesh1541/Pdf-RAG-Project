import React, { useEffect, useMemo, useState } from 'react'
import DocumentSidebar from './components/DocumentSidebar'
import ChatWindow from './components/ChatWindow'
import DashboardPanel from './components/DashboardPanel'
import EvaluationPanel from './components/EvaluationPanel'
import { api } from './services/api'

const TABS = ['chat', 'dashboard', 'evaluation']

export default function App() {
  const [documents, setDocuments] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [messages, setMessages] = useState([])
  const [conversations, setConversations] = useState([])
  const [currentConversation, setCurrentConversation] = useState(null)
  const [activeTab, setActiveTab] = useState('chat')
  const [dashboard, setDashboard] = useState(null)
  const [evaluationResult, setEvaluationResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [sidebarLoading, setSidebarLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [error, setError] = useState('')
  const [initializedConversation, setInitializedConversation] = useState(false)

  const selectedDocuments = useMemo(() => {
    if (selectedIds.length === 0) return documents.filter((doc) => doc.status === 'ready')
    return documents.filter((doc) => selectedIds.includes(doc.id))
  }, [documents, selectedIds])

  const loadAll = async () => {
    try {
      setSidebarLoading(true)
      const [docsRes, convRes, dashRes] = await Promise.all([
        api.getDocuments(),
        api.getConversations(),
        api.getDashboard(),
      ])
      setDocuments(docsRes.results || [])
      setConversations(convRes.results || [])
      setDashboard(dashRes)
      const readyIds = (docsRes.results || []).filter((doc) => doc.status === 'ready').map((doc) => doc.id)
      setSelectedIds((current) => (current.length ? current : readyIds))
    } catch (err) {
      setError(err.message)
    } finally {
      setSidebarLoading(false)
    }
  }

  useEffect(() => {
    loadAll()
  }, [])

  useEffect(() => {
    if (!initializedConversation && conversations.length > 0) {
      const latest = conversations[0]
      setCurrentConversation(latest.id)
      setMessages(latest.messages || [])
      setInitializedConversation(true)
    }
  }, [conversations, initializedConversation])

  const handleUpload = async (files) => {
    if (!files?.length) return
    setError('')
    try {
      setLoading(true)
      await api.uploadDocuments(files)
      await loadAll()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await api.deleteDocument(id)
      setDocuments((docs) => docs.filter((doc) => doc.id !== id))
      setSelectedIds((ids) => ids.filter((value) => value !== id))
      await loadAll()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleToggleDocument = (id) => {
    setSelectedIds((ids) => (ids.includes(id) ? ids.filter((value) => value !== id) : [...ids, id]))
  }

  const handleSend = async (text) => {
    setError('')
    setLoading(true)
    try {
      const response = await api.sendChat({
        message: text,
        conversation_id: currentConversation || undefined,
        document_ids: selectedIds,
      })
      setCurrentConversation(response.conversation.id)
      setMessages(response.conversation.messages || [])
      await loadAll()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleClearChat = () => {
    setMessages([])
    setCurrentConversation(null)
  }

  const handleNewConversation = () => {
    setMessages([])
    setCurrentConversation(null)
    setInitializedConversation(true)
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    setError('')
    try {
      const result = await api.searchDocuments(searchQuery)
      setActiveTab('dashboard')
      setDashboard((prev) => ({ ...(prev || {}), searchResults: result.results || [] }))
    } catch (err) {
      setError(err.message)
    }
  }

  const handleSelectConversation = async (conversationId) => {
    if (!conversationId) return
    try {
      const data = await api.getConversation(conversationId)
      setCurrentConversation(data.id)
      setMessages(data.messages || [])
      setActiveTab('chat')
      setInitializedConversation(true)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleEvaluate = async ({ question, expected_answer }) => {
    setError('')
    setLoading(true)
    try {
      const result = await api.evaluate({
        question,
        expected_answer,
        document_ids: selectedIds,
      })
      setEvaluationResult(result)
      setActiveTab('evaluation')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid h-screen grid-cols-[340px_1fr] bg-slate-950 text-slate-100">
      <DocumentSidebar
        documents={documents}
        selectedIds={selectedIds}
        onToggleDocument={handleToggleDocument}
        onUpload={handleUpload}
        onDelete={handleDelete}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSearch={handleSearch}
        loading={sidebarLoading}
      />

      <main className="flex min-h-0 flex-col overflow-hidden">
        <div className="flex items-center gap-2 border-b border-white/10 bg-slate-900/70 px-6 py-3 backdrop-blur">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${activeTab === tab ? 'bg-brand-500 text-white' : 'text-slate-300 hover:bg-white/5'}`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
          <div className="ml-auto text-sm text-slate-400">
            {selectedDocuments.length} document(s) selected
          </div>
        </div>

        {error && <div className="border-b border-rose-500/20 bg-rose-500/10 px-6 py-3 text-sm text-rose-200">{error}</div>}

        <div className="min-h-0 flex-1 overflow-y-auto">
          {activeTab === 'chat' && (
            <ChatWindow
              messages={messages}
              conversations={conversations}
              currentConversation={currentConversation}
              onSelectConversation={handleSelectConversation}
              onSend={handleSend}
              loading={loading}
              conversationTitle={conversations.find((conv) => conv.id === currentConversation)?.title}
              onClearChat={handleClearChat}
              onNewConversation={handleNewConversation}
            />
          )}
          {activeTab === 'dashboard' && <DashboardPanel dashboard={dashboard} />}
          {activeTab === 'evaluation' && (
            <EvaluationPanel loading={loading} onEvaluate={handleEvaluate} result={evaluationResult} />
          )}
        </div>
      </main>
    </div>
  )
}
