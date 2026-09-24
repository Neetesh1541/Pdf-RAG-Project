import React, { useState } from 'react'

export default function EvaluationPanel({ onEvaluate, loading, result }) {
  const [question, setQuestion] = useState('Compare the methodologies used in the uploaded papers.')
  const [expectedAnswer, setExpectedAnswer] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    await onEvaluate({ question, expected_answer: expectedAnswer })
  }

  return (
    <section className="space-y-6 p-6">
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-brand-300">RAG Evaluation</p>
        <h2 className="mt-2 text-2xl font-semibold text-white">Measure retrieval and answer quality</h2>
      </div>

      <form onSubmit={submit} className="grid gap-4 rounded-3xl border border-white/10 bg-white/5 p-5 shadow-soft">
        <div>
          <label className="text-sm text-slate-300">Sample question</label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none"
          />
        </div>
        <div>
          <label className="text-sm text-slate-300">Expected answer (optional)</label>
          <textarea
            value={expectedAnswer}
            onChange={(e) => setExpectedAnswer(e.target.value)}
            rows={3}
            className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-white outline-none"
          />
        </div>
        <button disabled={loading} className="w-fit rounded-2xl bg-brand-500 px-5 py-3 text-sm font-semibold text-white hover:bg-brand-400 disabled:opacity-50">
          Run evaluation
        </button>
      </form>

      {result && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Object.entries(result.metrics || {}).map(([key, value]) => (
            <div key={key} className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-soft">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{key.replaceAll('_', ' ')}</p>
              <p className="mt-2 text-xl font-semibold text-white">{String(value)}</p>
            </div>
          ))}
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-soft md:col-span-2 xl:col-span-3">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Answer</p>
            <p className="mt-2 whitespace-pre-wrap text-sm text-slate-100">{result.answer}</p>
          </div>
        </div>
      )}
    </section>
  )
}
