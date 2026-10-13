import { ChangeEvent, useReducer } from 'react'
import { analyze } from './api'
import { FindingCard } from './components/FindingCard'
import type { Report } from './types'
import styles from './App.module.scss'

const example = `2026 Budget Planner\n\nThe main PDF contains exactly 48 pages.\n\nIncludes both A4 and US Letter PDF editions.\n\nContains monthly budget review worksheets.\n\nIncludes savings goal trackers.`
type State = { description: string; file?: File; phase: 'IDLE'|'ANALYZING'|'SUCCESS'|'ERROR'; report?: Report; error?: string }
type Action = Partial<State>
function reducer(state: State, action: Action): State { return { ...state, ...action } }
function markdown(report: Report) { return report.findings.map(f => `## ${f.status}: ${f.claim.text}\n\n${f.reason}\n`).join('\n') }

export default function App() {
  const [state, dispatch] = useReducer(reducer, { description: '', phase: 'IDLE' })
  const choose = (event: ChangeEvent<HTMLInputElement>) => dispatch({ file: event.target.files?.[0] })
  async function submit() { if (!state.file || !state.description.trim()) return; dispatch({ phase: 'ANALYZING', error: undefined }); try { dispatch({ phase: 'SUCCESS', report: await analyze(state.description, state.file) }) } catch (error) { dispatch({ phase: 'ERROR', error: error instanceof Error ? error.message : 'Unexpected error' }) } }
  async function tryExample() { const response = await fetch('/examples/budget_planner_A4.pdf'); const blob = await response.blob(); dispatch({ description: example, file: new File([blob], 'budget_planner_A4.pdf', { type: 'application/pdf' }), phase: 'IDLE', report: undefined }) }
  return <main className={styles.app}><header><a className={styles.logo} href="/">PROMISE <i>/</i> DIFF</a><span>OPEN SOURCE · LOCAL-FIRST QA</span><a href="https://github.com" target="_blank">GITHUB ↗</a></header>
    <section className={styles.hero}><p>VERIFY WHAT YOU PROMISE BEFORE YOU SELL.</p><h1>Your listing makes promises.<br/><b>Do your files keep them?</b></h1><div>Check your digital downloads against your product description before publishing.</div></section>
    <section className={styles.inputs}><label>PRODUCT DESCRIPTION<textarea aria-label="Product description" value={state.description} onChange={e => dispatch({ description: e.target.value })} placeholder="Paste a listing: “Includes 120 printable pages…”" /></label><label>ACTUAL DOWNLOAD<input aria-label="Actual download" type="file" accept=".pdf,.zip,application/pdf,application/zip" onChange={choose}/><div className={styles.drop}>{state.file ? `${state.file.name} · ${(state.file.size / 1024).toFixed(1)} KB` : 'Drop a PDF or ZIP here\nMax 12 MB · PDFs only'}</div></label></section>
    <section className={styles.actions}><button className={styles.primary} disabled={state.phase === 'ANALYZING' || !state.file || !state.description.trim()} onClick={submit}>{state.phase === 'ANALYZING' ? 'VERIFYING…' : 'VERIFY PRODUCT'}</button><button onClick={tryExample}>TRY EXAMPLE</button><small>PDF / ZIP · Nothing is stored · Local Ollama inference</small></section>
    {state.error && <p className={styles.error}>{state.error}</p>}{state.report && <section className={styles.results}><div className={styles.resultHead}><p>WHAT YOU PROMISED <i>VS</i> WHAT YOU DELIVERED</p><button onClick={() => { const url = URL.createObjectURL(new Blob([markdown(state.report!)], {type:'text/markdown'})); const a = document.createElement('a'); a.href=url; a.download='promisediff-report.md'; a.click(); URL.revokeObjectURL(url) }}>EXPORT .MD</button></div><div className={styles.counts}>{Object.entries(state.report.summary).map(([name, count]) => <div key={name}><strong>{count}</strong><span>{name.replace('_', ' ')}</span></div>)}</div>{state.report.findings.map(f => <FindingCard key={f.claim.id} finding={f}/>)}</section>}</main>
}
