import React from 'react'

function MetricCard({ label, value, hint }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-soft">
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</p>
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
      {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
    </div>
  )
}

export default function DashboardPanel({ dashboard }) {
  const totals = dashboard?.totals || {}
  const searchResults = dashboard?.searchResults || []
  return (
    <section className="space-y-6 p-6">
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-brand-300">Operations Dashboard</p>
        <h2 className="mt-2 text-2xl font-semibold text-white">RAG health and usage</h2>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard label="Documents" value={totals.documents ?? 0} />
        <MetricCard label="Pages" value={totals.pages ?? 0} />
        <MetricCard label="Chunks" value={totals.chunks ?? 0} />
        <MetricCard label="Questions" value={totals.questions ?? 0} />
        <MetricCard label="Avg latency (ms)" value={totals.average_latency_ms ?? 0} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-soft">
          <h3 className="text-lg font-semibold text-white">Recent documents</h3>
          <div className="mt-4 space-y-3">
            {(dashboard?.recent_documents || []).map((doc) => (
              <div key={doc.id} className="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-sm">
                <div>
                  <p className="font-medium text-white">{doc.original_name}</p>
                  <p className="text-xs text-slate-400">{doc.status} • {doc.page_count} pages • {doc.chunk_count} chunks</p>
                </div>
                <span className="text-xs text-slate-500">{new Date(doc.uploaded_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-soft">
          <h3 className="text-lg font-semibold text-white">Recent conversations</h3>
          <div className="mt-4 space-y-3">
            {(dashboard?.recent_conversations || []).map((conversation) => (
              <div key={conversation.id} className="rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-sm">
                <p className="font-medium text-white">{conversation.title}</p>
                <p className="text-xs text-slate-400">{conversation.message_count} messages • {new Date(conversation.updated_at).toLocaleString()}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {searchResults.length > 0 && (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-soft">
          <h3 className="text-lg font-semibold text-white">Search results</h3>
          <div className="mt-4 space-y-3">
            {searchResults.map((doc) => (
              <div key={doc.document_id} className="rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-sm">
                <p className="font-medium text-white">{doc.filename}</p>
                <div className="mt-2 space-y-2 text-xs text-slate-400">
                  {doc.matches?.map((match) => (
                    <div key={match.chunk_id} className="rounded-xl border border-white/10 bg-white/5 p-3">
                      <div className="font-medium text-slate-200">Page {match.page_number}</div>
                      <p className="mt-1 text-slate-400">{match.snippet}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
