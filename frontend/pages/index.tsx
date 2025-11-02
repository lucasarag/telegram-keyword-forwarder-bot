import { useState, useEffect } from "react";
import { api } from "../lib/api";

export default function Home() {
  const [keyword, setKeyword] = useState("");
  const [chatId, setChatId] = useState("");
  const [status, setStatus] = useState<any>({});
  const [logs, setLogs] = useState<string[]>([]);

  const fetchStatus = async () => {
    const s = await api.getStatus();
    setStatus(s);
  };

  const fetchLogs = async () => {
    const l = await api.getLogs();
    setLogs(l);
  };

  useEffect(() => {
    fetchStatus();
    fetchLogs();
    const interval = setInterval(() => { fetchStatus(); fetchLogs(); }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleConfig = async () => {
    await api.config({ keyword, chat_id: Number(chatId) });
    fetchStatus();
  };

  const handleStart = async () => {
    await api.start();
    fetchStatus();
  };

  const handleStop = async () => {
    await api.stop();
    fetchStatus();
  };

  return (
    <div>
      <h2>Forward Config</h2>
      <input placeholder="Keyword" value={keyword} onChange={e => setKeyword(e.target.value)} />
      <input placeholder="Chat ID" value={chatId} onChange={e => setChatId(e.target.value)} />
      <button onClick={handleConfig}>Salvar Configuração</button>
      <button onClick={handleStart}>Start</button>
      <button onClick={handleStop}>Stop</button>

      <h3>Status</h3>
      <pre>{JSON.stringify(status, null, 2)}</pre>

      <h3>Logs</h3>
      <pre>{logs.join("\n")}</pre>
    </div>
  );
}
