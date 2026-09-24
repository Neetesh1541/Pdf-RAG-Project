import React, { useState } from 'react'

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-3xl rounded-2xl px-4 py-3 shadow-soft ${isUser ? 'bg-brand-600 text-white' : 'bg-white/5 text-slate-100 ring-1 ring-white/10'}`}>
        <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
        {message.citations?.length > 0 && !isUser && (
          <div className="mt-3 grid gap-2">
            {message.citations.map((cite, index) => (
              <a
                key={`${cite.document_id || 'citation'}-${index}`}
                className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2 text-xs text-slate-300 hover:border-brand-500/40 hover:text-white"
                href={cite.document_url || '#'}
                target="_blank"
                rel="noreferrer"
              >
                {cite.document_name || 'Source'} — Page {cite.page_number}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function ChatWindow({
  messages,
  conversations,
  currentConversation,
  onSelectConversation,
  onSend,
  loading,
  conversationTitle,
  onClearChat,
  onNewConversation,
}) {
  const [input, setInput] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return
    const value = input.trim()
    setInput('')
    await onSend(value)
  }

  return (
    <section className="flex h-full flex-1 flex-col bg-slate-950">
      <header className="flex flex-col gap-4 border-b border-white/10 px-6 py-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-brand-300">ChatGPT-style RAG</p>
          <h2 className="text-xl font-semibold text-white">{conversationTitle || 'New conversation'}</h2>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {conversations.length > 0 && (
            <select
              value={currentConversation || ''}
              onChange={(e) => onSelectConversation(e.target.value)}
              className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none"
            >
              <option value="">Recent conversations</option>
              {conversations.map((conversation) => (
                <option key={conversation.id} value={conversation.id}>
                  {conversation.title}
                </option>
              ))}
            </select>
          )}
          <button onClick={onClearChat} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-200 hover:bg-white/5">
            Clear chat
          </button>
          <button onClick={onNewConversation} className="rounded-xl bg-brand-500 px-3 py-2 text-sm font-semibold text-white hover:bg-brand-400">
            New conversation
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          {messages.length === 0 && (
            <div className="rounded-3xl border border-dashed border-white/10 bg-white/5 p-8 text-center text-slate-300">
              Ask about methodology, objectives, limitations, results, or compare multiple papers.
            </div>
          )}
          {messages.map((message) => (
            <MessageBubble key={message.id || `${message.role}-${message.created_at}`} message={message} />
          ))}
          {loading && <div className="text-sm text-slate-400">ResearchMind is retrieving evidence…</div>}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="border-t border-white/10 p-4">
        <div className="mx-auto flex max-w-4xl gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={2}
            placeholder="Ask about uploaded documents…"
            className="min-h-[56px] flex-1 resize-none rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-2xl bg-brand-500 px-5 py-3 text-sm font-semibold text-white hover:bg-brand-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </form>
    </section>
  )
}
