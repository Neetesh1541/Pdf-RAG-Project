import React from 'react'

function statusTone(status) {
  switch (status) {
    case 'ready':
      return 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30'
    case 'processing':
      return 'bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/30'
    case 'failed':
      return 'bg-rose-500/15 text-rose-300 ring-1 ring-rose-500/30'
    default:
      return 'bg-slate-500/15 text-slate-300 ring-1 ring-slate-500/30'
  }
}

export default function DocumentSidebar({
  documents,
  selectedIds,
  onToggleDocument,
  onUpload,
  onDelete,
  searchQuery,
  onSearchChange,
  onSearch,
  loading,
}) {
  return (
    <aside className="flex h-full flex-col border-r border-white/10 bg-slate-900/90 backdrop-blur">
      <div className="border-b border-white/10 p-4">
        <div className="flex items-center justify-between gap-2">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-brand-300">ResearchMind AI</p>
            <h1 className="text-lg font-semibold text-white">Documents</h1>
          </div>
          <label className="cursor-pointer rounded-xl bg-brand-500 px-3 py-2 text-xs font-semibold text-white shadow-soft hover:bg-brand-400">
            Upload
            <input multiple type="file" accept="application/pdf" className="hidden" onChange={(e) => onUpload(e.target.files)} />
          </label>
        </div>
        <div className="mt-4 flex gap-2">
          <input
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSearch()}
            placeholder="Search documents..."
            className="w-full rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-500"
          />
          <button onClick={onSearch} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-200 hover:bg-white/5">
            Go
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {loading && <div className="rounded-xl border border-white/10 p-4 text-sm text-slate-300">Loading documents…</div>}
        {!loading && documents.length === 0 && (
          <div className="rounded-xl border border-dashed border-white/10 p-4 text-sm text-slate-400">
            Upload research papers, reports, and PDFs to begin.
          </div>
        )}
        <div className="space-y-3">
          {documents.map((doc) => (
            <article key={doc.id} className="rounded-2xl border border-white/10 bg-white/5 p-3 shadow-soft">
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(doc.id)}
                  onChange={() => onToggleDocument(doc.id)}
                  className="mt-1 h-4 w-4 rounded border-white/20 bg-slate-900 text-brand-500"
                />
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="truncate text-sm font-medium text-white">{doc.original_name}</h3>
                      <p className="text-xs text-slate-400">{new Date(doc.uploaded_at).toLocaleString()}</p>
                    </div>
                    <span className={`rounded-full px-2 py-1 text-[11px] font-medium ${statusTone(doc.status)}`}>
                      {doc.status}
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-slate-400">
                    <div>Pages<br /><span className="text-slate-100">{doc.page_count}</span></div>
                    <div>Chunks<br /><span className="text-slate-100">{doc.chunk_count}</span></div>
                    <div>Size<br /><span className="text-slate-100">{(doc.file_size / 1024 / 1024).toFixed(1)} MB</span></div>
                  </div>
                  {doc.error_message && <p className="mt-2 text-xs text-rose-300">{doc.error_message}</p>}
                </div>
              </div>
              <div className="mt-3 flex justify-end">
                <button onClick={() => onDelete(doc.id)} className="text-xs text-slate-400 hover:text-rose-300">
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      </div>
    </aside>
  )
}
