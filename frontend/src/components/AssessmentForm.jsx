import { useState } from 'react'
import axios from 'axios'

const symptoms = [
  { key: 'PainlessBlurryVision', label: 'ตามัวลงเรื่อย ๆ', detail: 'Painless blurry vision', icon: '👁️' },
  { key: 'AsymptomaticEarly', label: 'ระยะแรกไม่มีอาการเตือน', detail: 'Asymptomatic early', icon: '🔎' },
  { key: 'NightVisionLoss', label: 'มองเห็นแย่ลงในที่มืด', detail: 'Night vision loss', icon: '🌙' },
  { key: 'TunnelVision', label: 'ลานสายตาแคบลง', detail: 'Tunnel vision', icon: '🌀' },
  { key: 'RainbowHalos', label: 'เห็นวงรุ้งรอบดวงไฟ', detail: 'Rainbow halos', icon: '🌈' },
  { key: 'CentralDistortion', label: 'ภาพตรงกลางบิดเบี้ยว', detail: 'Central distortion', icon: '〰️' },
  { key: 'Floaters', label: 'เห็นจุดดำหรือหยากไย่', detail: 'Floaters', icon: '✨' },
]

const sexLabels = { female: 'หญิง', male: 'ชาย', other: 'อื่น ๆ / ไม่ระบุ' }
const emptySymptoms = Object.fromEntries(symptoms.map(({ key }) => [key, null]))
const historyStorageKey = 'eye-expert-patient-history'

function readHistory() {
  try {
    const savedHistory = JSON.parse(localStorage.getItem(historyStorageKey) || '[]')
    return Array.isArray(savedHistory) ? savedHistory : []
  } catch (storageError) {
    console.error('Unable to read patient history from browser storage.', storageError)
    return []
  }
}

function getHistoryDiagnosis(entry) {
  if (entry.primary_diagnosis) {
    return entry.primary_diagnosis
  }

  if (entry.cf_result?.primary_diagnosis) {
    return entry.cf_result.primary_diagnosis
  }

  if (entry.dataset_result?.primary_diagnosis) {
    return entry.dataset_result.primary_diagnosis
  }

  return 'ผลเดิม (ไม่มีข้อมูลอาการสำหรับคำนวณใหม่)'
}

export default function AssessmentForm() {
  const [patient, setPatient] = useState({ name: '', age: '', sex: '' })
  const [answers, setAnswers] = useState(emptySymptoms)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState(readHistory)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handlePatientChange = (event) => {
    setPatient({ ...patient, [event.target.name]: event.target.value })
  }

  const handleAnswerChange = (event) => {
    const { name, value } = event.target
    setAnswers({ ...answers, [name]: value === '' ? null : Number(value) })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await axios.post('/api/diagnose', {
        ...patient,
        age: Number(patient.age),
        ...answers,
      })
      const nextResult = { ...response.data, assessed_at: new Date().toISOString() }
      const nextHistory = [nextResult, ...history].slice(0, 10)

      setResult(nextResult)
      setHistory(nextHistory)
      try {
        localStorage.setItem(historyStorageKey, JSON.stringify(nextHistory))
      } catch (storageError) {
        console.error('Unable to save patient history to browser storage.', storageError)
        setError('บันทึกผลประเมินแล้ว แต่จัดเก็บประวัติในเบราว์เซอร์ไม่สำเร็จ')
      }
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'เชื่อมต่อระบบประเมินไม่สำเร็จ กรุณาตรวจสอบว่า backend เปิดอยู่')
    } finally {
      setLoading(false)
    }
  }

  const confidence = result ? result.dataset_result.confidence_pct : 0
  const hasActivatedRules = Boolean(result?.cf_result.activated_rules.length)

  return (
    <main className="assessment-shell">
      <section className="assessment-card">
        <form className="assessment-form" onSubmit={handleSubmit}>
          <section className="form-section patient-section" aria-labelledby="patient-heading">
            <div className="section-heading">
              <span className="section-icon" aria-hidden="true">♟</span>
              <h1 id="patient-heading">ข้อมูลผู้ป่วย</h1>
            </div>
            <div className="patient-fields">
              <label className="field-label patient-name">
                ชื่อ-นามสกุล
                <input name="name" value={patient.name} onChange={handlePatientChange} autoComplete="name" maxLength={120} required />
              </label>
              <label className="field-label">
                อายุ
                <input name="age" type="number" min="1" max="120" value={patient.age} onChange={handlePatientChange} inputMode="numeric" required />
              </label>
              <label className="field-label">
                เพศ
                <select name="sex" value={patient.sex} onChange={handlePatientChange} required>
                  <option value="" disabled>เลือกเพศ</option>
                  <option value="female">หญิง</option>
                  <option value="male">ชาย</option>
                  <option value="other">อื่น ๆ / ไม่ระบุ</option>
                </select>
              </label>
            </div>
          </section>

          <section className="form-section symptom-section" aria-labelledby="symptoms-heading">
            <div className="section-heading">
              <span className="section-icon" aria-hidden="true">☷</span>
              <h2 id="symptoms-heading">ประเมินอาการทางตา</h2>
            </div>
            <div className="symptom-list">
              {symptoms.map((symptom) => (
                <label className="symptom-field" key={symptom.key}>
                  <span className="symptom-label">
                    <span className="symptom-emoji" aria-hidden="true">{symptom.icon}</span>
                    <span>{symptom.label} <small>({symptom.detail})</small></span>
                  </span>
                  <select
                    name={symptom.key}
                    value={answers[symptom.key] === null ? '' : String(answers[symptom.key])}
                    onChange={handleAnswerChange}
                    required
                  >
                    <option value="" disabled>เลือกคำตอบ</option>
                    <option value="1">มีอาการ</option>
                    <option value="0">ไม่มีอาการ</option>
                  </select>
                </label>
              ))}
            </div>
          </section>

          <p className="medical-note">ผลนี้เป็นการคัดกรองจากข้อมูลตัวอย่าง ไม่ใช่การวินิจฉัยแทนจักษุแพทย์</p>
          {error && <p className="form-error" role="alert">{error}</p>}
          <div className="form-actions">
            <button className="submit-button" type="submit" disabled={loading}>
              <span aria-hidden="true">▦</span>
              {loading ? 'กำลังประมวลผล…' : 'ประมวลผลการวินิจฉัย'}
            </button>
            <a className="history-button" href="#patient-history">
              <span aria-hidden="true">↶</span>
              ดูประวัติผู้ป่วย
            </a>
          </div>
        </form>
      </section>

      <aside className="results-column" aria-label="สรุปผลการวิเคราะห์">
        <section className="result-panel diagnosis-panel" aria-live="polite">
          <p className="panel-kicker">ผลสรุปการวิเคราะห์</p>
          {result ? (
            <>
              <div className="cf-result">
                <div className="cf-result-heading">
                  <div>
                    <p className="cf-eyebrow">
                      {hasActivatedRules ? 'ผลตามกฎที่ตรงกับอาการ' : 'ผลการประเมินตามกฎ'}
                    </p>
                    <h2>{result.primary_diagnosis}</h2>
                    {hasActivatedRules ? (
                      <p className="cf-caveat">
                        เทียบข้อมูลตัวอย่าง: {result.dataset_result.primary_diagnosis}
                      </p>
                    ) : (
                      <p className="cf-caveat">
                        ไม่มีเงื่อนไขในกฎที่ตรงกับอาการ ไม่ได้ยืนยันว่าไม่มีโรค หากยังกังวลควรพบจักษุแพทย์
                      </p>
                    )}
                  </div>
                  {hasActivatedRules && (
                    <strong className="cf-final">ตรงกัน {confidence.toFixed(1)}%</strong>
                  )}
                </div>
              </div>
              {hasActivatedRules && (
                <>
                  <div
                    className="cf-meter"
                    role="progressbar"
                    aria-label="เปอร์เซ็นต์ตัวอย่างของโรคที่ตรงกัน"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-valuenow={confidence.toFixed(1)}
                  >
                    <span style={{ width: `${confidence}%` }} />
                  </div>
                  {result.dataset_result.matches.length > 0 ? (
                    <ol className="cf-disease-list">
                      {result.dataset_result.matches.map((disease) => (
                        <li key={disease.disease}>
                          <span>{disease.disease_th}</span>
                          <strong>{disease.percentage.toFixed(1)}% ({disease.records} รายการ)</strong>
                        </li>
                      ))}
                    </ol>
                  ) : (
                    <p className="cf-empty">ไม่พบข้อมูลตัวอย่างที่ใกล้เคียง</p>
                  )}
                  <p className="cf-caveat">เทียบจากข้อมูลตัวอย่างใกล้เคียง {result.dataset_result.matched_record_count} รายการ ผลนี้ไม่ใช่การวินิจฉัยทางการแพทย์</p>
                </>
              )}
            </>
          ) : (
            <div className="empty-result">
              <span aria-hidden="true">◉</span>
              <p>กรอกข้อมูลและประเมินอาการ<br />เพื่อดูผลการวิเคราะห์</p>
            </div>
          )}
        </section>

        <section className="result-panel rules-panel" aria-labelledby="rules-heading">
          <div className="panel-heading">
            <span className="section-icon" aria-hidden="true">♧</span>
            <h2 id="rules-heading">Activated Rules (กฎที่ถูกกระตุ้น)</h2>
          </div>
          {result?.cf_result.activated_rules.length ? (
            <ul className="activated-rule-list">
              {result.cf_result.activated_rules.map((rule) => (
                <li key={rule.rule_id}>
                  <strong>{rule.rule_id} · {rule.disease_th}</strong>
                  <span>เงื่อนไข: {rule.description}</span>
                  <small>Support {rule.support_pct.toFixed(2)}% · Confidence / CF(rule) {rule.confidence_pct.toFixed(2)}%</small>
                </li>
              ))}
            </ul>
          ) : (
            <p className="panel-empty">{result ? 'ไม่มีกฎที่ตรงกับอาการชุดนี้' : 'กฎที่ตรงกับอาการจะแสดงที่นี่หลังประเมิน'}</p>
          )}
        </section>

        <section className="result-panel history-panel" id="patient-history" aria-labelledby="history-heading">
          <div className="panel-heading history-heading">
            <span className="section-icon" aria-hidden="true">▤</span>
            <h2 id="history-heading">ประวัติผู้ป่วย</h2>
            <span className="history-count">ล่าสุด {history.length} รายการ</span>
          </div>
          <div className="history-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ชื่อ</th>
                  <th>อายุ</th>
                  <th>เพศ</th>
                  <th>โรค</th>
                  <th>ตรงกับข้อมูล</th>
                  <th>วันที่</th>
                </tr>
              </thead>
              <tbody>
                {history.length ? history.map((entry, index) => (
                  <tr key={`${entry.assessed_at}-${index}`}>
                    <td>{entry.patient.name}</td>
                    <td>{entry.patient.age}</td>
                    <td>{sexLabels[entry.patient.sex]}</td>
                    <td>{getHistoryDiagnosis(entry)}</td>
                    <td>
                      {entry.cf_result?.activated_rules?.length
                        ? `${entry.dataset_result.confidence_pct.toFixed(1)}%`
                        : '—'}
                    </td>
                    <td>{new Date(entry.assessed_at).toLocaleDateString('th-TH')}</td>
                  </tr>
                )) : (
                  <tr><td className="history-empty" colSpan="6">ยังไม่มีประวัติผู้ป่วย</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </aside>
    </main>
  )
}
