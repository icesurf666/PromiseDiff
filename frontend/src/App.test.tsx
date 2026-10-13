import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'

const report = {
  summary: { supported: 1, contradicted: 0, unverified: 0, out_of_scope: 0 },
  warnings: [],
  findings: [{
    claim: { id: '1', text: '48 pages', type: 'PAGE_COUNT', source_quote: '48 pages' },
    status: 'SUPPORTED' as const, method: 'DETERMINISTIC' as const,
    reason: 'Observed page count is 48.', evidence: [],
  }],
}

describe('PromiseDiff form', () => {
  beforeEach(() => { vi.restoreAllMocks() })
  afterEach(cleanup)

  it('prevents submission until both required inputs exist', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: 'VERIFY PRODUCT' })).toBeDisabled()
  })

  it('submits the selected file and renders findings', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => report }))
    render(<App />)
    await userEvent.type(screen.getByLabelText('Product description'), 'Includes 48 pages.')
    const input = screen.getByLabelText('Actual download') as HTMLInputElement
    fireEvent.change(input, { target: { files: [new File(['pdf'], 'planner.pdf', { type: 'application/pdf' })] } })
    await userEvent.click(screen.getByRole('button', { name: 'VERIFY PRODUCT' }))
    expect(await screen.findByText('48 pages')).toBeInTheDocument()
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/analyze'), expect.objectContaining({ method: 'POST' }))
  })

  it('shows a truthful loading state and an API error', async () => {
    let reject!: (error: Error) => void
    vi.stubGlobal('fetch', vi.fn().mockReturnValue(new Promise((_, fail) => { reject = fail })))
    render(<App />)
    await userEvent.type(screen.getByLabelText('Product description'), 'Includes 48 pages.')
    fireEvent.change(screen.getByLabelText('Actual download'), { target: { files: [new File(['pdf'], 'planner.pdf')] } })
    await userEvent.click(screen.getByRole('button', { name: 'VERIFY PRODUCT' }))
    expect(screen.getByRole('button', { name: 'VERIFYING…' })).toBeDisabled()
    reject(new Error('Ollama is unavailable'))
    expect(await screen.findByText('Ollama is unavailable')).toBeInTheDocument()
  })

  it('reveals evidence and exposes the Markdown export', async () => {
    const evidenceReport = { ...report, findings: [{ ...report.findings[0], evidence: [{ kind: 'DOCUMENT_TEXT' as const, filename: 'planner.pdf', page: 1, quote: 'Budget review' }] }] }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => evidenceReport }))
    render(<App />)
    await userEvent.type(screen.getByLabelText('Product description'), 'Includes 48 pages.')
    fireEvent.change(screen.getByLabelText('Actual download'), { target: { files: [new File(['pdf'], 'planner.pdf')] } })
    await userEvent.click(screen.getByRole('button', { name: 'VERIFY PRODUCT' }))
    await userEvent.click(await screen.findByRole('button', { name: /48 pages/i }))
    expect(screen.getByText('Budget review')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'EXPORT .MD' })).toBeInTheDocument()
  })

  it('shows analysis coverage warnings', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ ...report, warnings: ['Only 12 pages were reviewed.'] }) }))
    render(<App />)
    await userEvent.type(screen.getByLabelText('Product description'), 'Includes 48 pages.')
    fireEvent.change(screen.getByLabelText('Actual download'), { target: { files: [new File(['pdf'], 'planner.pdf')] } })
    await userEvent.click(screen.getByRole('button', { name: 'VERIFY PRODUCT' }))
    expect(await screen.findByText('Only 12 pages were reviewed.')).toBeInTheDocument()
  })

  it('rejects oversized client-side uploads', async () => {
    render(<App />)
    const oversized = new File([new Uint8Array(12 * 1024 * 1024 + 1)], 'huge.pdf')
    fireEvent.change(screen.getByLabelText('Actual download'), { target: { files: [oversized] } })
    expect(await screen.findByText('Upload exceeds the 12 MB limit')).toBeInTheDocument()
  })
})
