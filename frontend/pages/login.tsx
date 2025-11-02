import { useState } from "react";
import { api } from "../lib/api";

export default function Login() {
  const [apiId, setApiId] = useState("");
  const [apiHash, setApiHash] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async () => {
    try {
      const res = await api.login({ api_id: Number(apiId), api_hash: apiHash, phone });
      setMessage(res.message);
      // Aqui você pode redirecionar para a tela de configuração
    } catch (err: any) {
      setMessage(err.message || "Erro no login");
    }
  };

  return (
    <div>
      <h2>Login Telegram</h2>
      <input placeholder="API ID" value={apiId} onChange={e => setApiId(e.target.value)} />
      <input placeholder="API Hash" value={apiHash} onChange={e => setApiHash(e.target.value)} />
      <input placeholder="Telefone" value={phone} onChange={e => setPhone(e.target.value)} />
      <button onClick={handleLogin}>Login / Gerar Session</button>
      {message && <p>{message}</p>}
    </div>
  );
}
