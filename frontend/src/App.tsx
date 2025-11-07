import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api'
type Status = { is_logged: boolean; keywords: string[]; chat_id: number | string | null }
export default function App() {
  const [step, setStep] = useState<'login' | 'code' | 'dash'>('login')
  const [apiId, setApiId] = useState('')
  const [apiHash, setApiHash] = useState('')
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [keywords, setKeywords] = useState('')
  const [chatId, setChatId] = useState('')
  const [logs, setLogs] = useState<string[]>([])
  const logRef = useRef<HTMLTextAreaElement>(null)
  useEffect(() => { api<Status>('/api/status').then(s => {
      if (s.is_logged) setStep('dash')
      setKeywords((s.keywords || []).join(', '))
      setChatId((s.chat_id ?? '').toString())
    }).catch(() => {}) }, [])
  useEffect(() => { if (step === 'dash') {
      const ws = new WebSocket((location.origin.replace('http','ws')) + '/api/ws/logs')
      ws.onmessage = (ev) => setLogs(prev => [...prev.slice(-999), ev.data])
      return () => ws.close()
  }}, [step])
  useEffect(() => { if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight }, [logs])
  async function handleStart() {
    setBusy(true)
    try {
      const res = await api<any>('/api/login/start', {
        method: 'POST',
        body: JSON.stringify({ api_id: Number(apiId), api_hash: apiHash, phone: phone || null })
      })
      if (res.status === 'phone_required') alert('Informe o número de telefone do Telegram (ex.: +5511999999999).')
      if (res.status === 'already_logged' || res.status === 'code_sent') setStep('code')
    } finally { setBusy(false) }
  }
  async function handleConfirm() {
    setBusy(true)
    try {
      const res = await api<any>('/api/login/confirm', {
        method: 'POST',
        body: JSON.stringify({ code, phone: phone || null })
      })
      if (res.status === 'password_required') {
        const pwd = prompt('2FA habilitado. Digite a senha:')
        if (pwd) {
          await api('/api/login/confirm', { method:'POST', body:JSON.stringify({ code, phone:phone||null, password:pwd }) })
        }
      }
      if (res.error) {
        alert(`Erro: ${res.error}`)
        return
      }
      // Check status after login attempt
      const st = await api<Status>('/api/status')
      if (st.is_logged) {
        setStep('dash')
      } else {
        alert('Falha ao autenticar. Verifique o código e tente novamente.')
      }
    } catch (err: any) {
      alert(`Erro: ${err.message || 'Falha na comunicação com o servidor'}`)
    } finally {
      setBusy(false)
    }
  }
  async function handleSave() {
    setBusy(true)
    try {
      const payload = { keywords: keywords.split(',').map(s=>s.trim()).filter(Boolean), chat_id: chatId||null }
      await api('/api/settings', { method:'POST', body:JSON.stringify(payload) })
      alert('Configurações salvas!')
    } finally { setBusy(false) }
  }
  return (<div className="container">
    <h1>Encaminhador de Mensagens</h1>
    {step==='login' && (<div className="card">
      <div className="row">
        <div><div className="label">API ID</div>
        <input className="input" value={apiId} onChange={e=>setApiId(e.target.value)} placeholder="Digite seu API ID"/></div>
        <div><div className="label">API HASH</div>
        <input className="input" value={apiHash} onChange={e=>setApiHash(e.target.value)} placeholder="Digite seu API HASH"/></div>
        <div><div className="label">Telefone (ex.: +5511999999999)</div>
        <input className="input" value={phone} onChange={e=>setPhone(e.target.value)} placeholder="Número do Telegram"/></div>
        <div style={{alignSelf:'flex-end'}}><button disabled={busy} className="button" onClick={handleStart}>Conectar</button></div>
      </div></div>)}
    {step==='code' && (<div className="card"><div className="row"><span className="badge">Aguardando o código enviado pelo Telegram</span></div>
      <div className="row" style={{marginTop:12}}><input className="input" value={code} onChange={e=>setCode(e.target.value)} placeholder="Digite o código"/>
        <button disabled={busy} className="button" onClick={handleConfirm}>Enviar</button></div></div>)}
    {step==='dash' && (<div className="card"><div className="row">
      <div style={{flex:1}}><div className="label">Keywords</div>
      <input className="input" style={{width:'100%'}} value={keywords} onChange={e=>setKeywords(e.target.value)}/></div>
      <div style={{width:280}}><div className="label">Chat ID destino</div>
      <input className="input" value={chatId} onChange={e=>setChatId(e.target.value)}/></div>
      <div style={{alignSelf:'flex-end'}}><button disabled={busy} className="button" onClick={handleSave}>Salvar</button></div>
    </div><div className="row" style={{marginTop:24}}><div style={{flex:1}}><h2 className="h2">Logs</h2>
      <textarea ref={logRef} className="textarea" readOnly value={logs.join('\n')}/></div></div></div>)}
  </div>)
}