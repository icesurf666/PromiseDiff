import type { Report } from './types'
const base = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
export async function analyze(description: string, file: File): Promise<Report> {
  const data = new FormData(); data.append('description', description); data.append('file', file)
  const response = await fetch(`${base}/api/analyze`, { method: 'POST', body: data })
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail ?? 'Analysis failed') }
  return response.json() as Promise<Report>
}
