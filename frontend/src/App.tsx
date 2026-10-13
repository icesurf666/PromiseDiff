import { ChangeEvent, DragEvent, useReducer } from 'react'
import { analyze } from './api'
import { FindingCard } from './components/FindingCard'
import type { Report } from './types'
import styles from './App.module.scss'

const example = `2026 Budget Planner\n\nThe main PDF contains exactly 48 pages.\n\nIncludes both A4 and US Letter PDF editions.\n\nContains monthly budget review worksheets.\n\nIncludes savings goal trackers.`
const MAX_UPLOAD = 12 * 1024 * 1024
const githubUrl = import.meta.env.VITE_GITHUB_URL
type State = { description: string; file?: File; phase: 'IDLE'|'ANALYZING'|'SUCCESS'|'ERROR'; report?: Report; error?: string }
type Action = Partial<State>
function reducer(state: State, action: Action): State { return { ...state, ...action } }
function markdown(report: Report) { return report.findings.map(f => `## ${f.status}: ${f.claim.text}\n\n${f.reason}\n`).join('\n') }

export default function App() {
  const [state, dispatch] = useReducer(reducer, { description: '', phase: 'IDLE' })
  function selectFile(file?: File) { if (!file) return; if (file.size > MAX_UPLOAD) { dispatch({ phase: 'ERROR', error: 'Upload exceeds the 12 MB limit' }); return } if (!/\.(pdf|zip)$/i.test(file.name)) { dispatch({ phase: 'ERROR', error: 'Upload must be a PDF or ZIP' }); return } dispatch({ file, phase: 'IDLE', error: undefined, report: undefined }) }
  const choose = (event: ChangeEvent<HTMLInputElement>) => selectFile(event.target.files?.[0])
  const drop = (event: DragEvent<HTMLLabelElement>) => { event.preventDefault(); selectFile(event.dataTransfer.files[0]) }
  async function submit() { if (!state.file || !state.description.trim()) return; dispatch({ phase: 'ANALYZING', error: undefined }); try { dispatch({ phase: 'SUCCESS', report: await analyze(state.description, state.file) }) } catch (error) { dispatch({ phase: 'ERROR', error: error instanceof Error ? error.message : 'Unexpected error' }) } }
  async function tryExample() { try { const response = await fetch('/examples/budget_planner_A4.pdf'); if (!response.ok) throw new Error('Example PDF could not be loaded'); const blob = await response.blob(); dispatch({ description: example, file: new File([blob], 'budget_planner_A4.pdf', { type: 'application/pdf' }), phase: 'IDLE', report: undefined, error: undefined }) } catch (error) { dispatch({ phase: 'ERROR', error: error instanceof Error ? error.message : 'Example could not be loaded' }) } }
  return <main className={styles.app}><header><a className={styles.logo} href="/">PROMISE <i>/</i> DIFF</a><span>OPEN SOURCE · LOCAL-FIRST QA</span>{githubUrl && <a href={githubUrl} target="_blank" rel="noreferrer">GITHUB ↗</a>}</header>
    <section className={styles.hero}><p>CHECK THE LISTING BEFORE THE CUSTOMER DOES.</p><h1>Your listing says a lot.<br/><b>Make sure the files back it up.</b></h1><div>Compare a digital download with its product description before you publish.</div></section>
    <section className={styles.inputs}><label>PRODUCT DESCRIPTION<textarea aria-label="Product description" value={state.description} onChange={e => dispatch({ description: e.target.value })} placeholder="Paste a listing: “Includes 120 printable pages…”" /></label><label onDragOver={event => event.preventDefault()} onDrop={drop}>ACTUAL DOWNLOAD<input aria-label="Actual download" type="file" accept=".pdf,.zip,application/pdf,application/zip" onChange={choose}/><div className={styles.drop}>{state.file ? `${state.file.name} · ${(state.file.size / 1024).toFixed(1)} KB` : 'Drop a PDF or ZIP here\nUp to 12 MB · PDFs only'}</div></label></section>
    <section className={styles.actions}><button className={styles.primary} disabled={state.phase === 'ANALYZING' || !state.file || !state.description.trim()} onClick={submit}>{state.phase === 'ANALYZING' ? 'VERIFYING…' : 'VERIFY PRODUCT'}</button><button onClick={tryExample}>TRY EXAMPLE</button><small>PDF / ZIP · Files are not saved · Local Ollama inference</small></section>
    {state.error && <p className={styles.error}>{state.error}</p>}{state.report && <section className={styles.results}><div className={styles.resultHead}><p>WHAT THE LISTING SAYS <i>VS</i> WHAT THE FILES SHOW</p><button onClick={() => { const url = URL.createObjectURL(new Blob([markdown(state.report!)], {type:'text/markdown'})); const a = document.createElement('a'); a.href=url; a.download='promisediff-report.md'; a.click(); URL.revokeObjectURL(url) }}>EXPORT .MD</button></div>{state.report.warnings.map(warning => <p className={styles.warning} key={warning}>{warning}</p>)}<div className={styles.counts}>{Object.entries(state.report.summary).map(([name, count]) => <div key={name}><strong>{count}</strong><span>{name.replace('_', ' ')}</span></div>)}</div>{state.report.findings.map(f => <FindingCard key={f.claim.id} finding={f}/>)}</section>}</main>
}
