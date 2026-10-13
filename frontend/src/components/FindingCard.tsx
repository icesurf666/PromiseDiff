import { useState } from 'react'
import { motion } from 'motion/react'
import type { Finding } from '../types'
import styles from './FindingCard.module.scss'
export function FindingCard({ finding }: { finding: Finding }) {
  const [open, setOpen] = useState(false)
  return <motion.article className={`${styles.card} ${styles[finding.status]}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
    <button onClick={() => setOpen(!open)} aria-expanded={open} className={styles.toggle}><span>{finding.status.replace('_', ' ')}</span><strong>{finding.claim.source_quote}</strong><em>{finding.method}</em></button>
    <p>{finding.reason}</p>{open && <div className={styles.evidence}>{finding.evidence.length ? finding.evidence.map((item, i) => <div key={i}><code>{item.filename}</code>{item.kind === 'DOCUMENT_TEXT' ? <><code> · page {item.page}</code><blockquote>{item.quote}</blockquote></> : <code> · {item.property}: expected {String(item.expected)}, found {String(item.observed)}</code>}</div>) : 'No supporting evidence was recorded.'}</div>}
  </motion.article>
}
