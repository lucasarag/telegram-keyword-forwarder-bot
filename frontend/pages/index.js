import { useState, useEffect } from "react";
import ConfigPanel from "../components/ConfigPanel";
import LogViewer from "../components/LogViewer";

export default function Home() {
  const [apiId, setApiId] = useState("");
  const [apiHash, setApiHash] = useState("");
  const [phone, setPhone] = useState("");
  const [keyword, setKeyword] = useState("");
  const [chatId, setChatId] = useState("");
  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const backendUrl = process.env.NEXT_PUBLIC_API_URL;

  const handleLogin = async () => {
    const res = await fetch(`${backendUrl}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_id: Number(apiId), api_hash: apiHash, phone }),
    });
    if (res.ok) setIsLoggedIn(true);
  };

  const handleConfig = async () => {
    await fetch(`${backendUrl}/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keyword, chat_id: Number(chatId) }),
    });
  };

  const handleStart = async () => {
    await fetch(`${backendUrl}/start`, { method: "POST" });
    setIsRunning(true);
  };

  const handleStop = async () => {
    await fetch(`${backendUrl}/stop`, { method: "POST" });
    setIsRunning(false);
  };

  const fetchLogs = async () => {
    const res = await fetch(`${backendUrl}/logs`);
    if (res.ok) {
      const data = await res.json();
      setLogs(data.reverse());
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchLogs, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 text-gray-800 flex flex-col items-center py-8">
      <h1 className="text-3xl font-bold mb-6">Telegram Forward Control Panel</h1>

      {!isLoggedIn ? (
        <div className="bg-white shadow-md rounded-xl p-6 w-96">
          <h2 className="text-xl font-semibold mb-3">Login no Telegram</h2>
          <input
            className="input"
            placeholder="API ID"
            value={apiId}
            onChange={(e) => setApiId(e.target.value)}
          />
          <input
            className="input"
            placeholder="API Hash"
            value={apiHash}
            onChange={(e) => setApiHash(e.target.value)}
          />
          <input
            className="input"
            placeholder="Telefone (+55...)"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
          <button className="btn-primary mt-4 w-full" onClick={handleLogin}>
            Fazer Login
          </button>
        </div>
      ) : (
        <>
          <ConfigPanel
            keyword={keyword}
            chatId={chatId}
            setKeyword={setKeyword}
            setChatId={setChatId}
            handleConfig={handleConfig}
          />
          <div className="flex gap-3 mt-4">
            {!isRunning ? (
              <button className="btn-primary" onClick={handleStart}>
                ▶️ Iniciar
              </button>
            ) : (
              <button className="btn-stop" onClick={handleStop}>
                ⏹️ Parar
              </button>
            )}
          </div>
          <LogViewer logs={logs} />
        </>
      )}
    </div>
  );
}
