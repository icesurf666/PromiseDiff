export type Status = 'SUPPORTED' | 'CONTRADICTED' | 'UNVERIFIED' | 'OUT_OF_SCOPE'
export type Evidence = { kind: 'DOCUMENT_TEXT'; filename: string; page: number; quote: string } | { kind: 'FILE_METADATA'; filename: string; property: string; expected?: unknown; observed: unknown }
export type Finding = { claim: { id: string; text: string; type: string; source_quote: string }; status: Status; method: 'DETERMINISTIC' | 'SEMANTIC' | 'NONE'; reason: string; evidence: Evidence[] }
export type Report = { summary: Record<'supported' | 'contradicted' | 'unverified' | 'out_of_scope', number>; findings: Finding[]; warnings: string[] }
