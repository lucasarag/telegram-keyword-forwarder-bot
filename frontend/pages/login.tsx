import { useState } from "react";
import { login } from "../src/app/api";

export default function LoginPage() {
  const [apiId, setApiId] = useState("");
  const [apiHash, setApiHash] = useState("");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [codeRequired, setCodeRequired] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleLogin = async () => {
    setLoading(true);
    setMessage("");
    try {
      const res = await login(Number(apiId), apiHash, phone, codeRequired ? code : undefined);
      setMessage(res.message);
      if (!codeRequired && res.message.includes("Código")) setCodeRequired(true);
    } catch (err: any) {
      setMessage(err.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 400, margin: "auto", padding: 20 }}>
      <h1>Login Telegram</h1>
      <input placeholder="API ID" value={apiId} onChange={e => setApiId(e.target.value)} />
      <input placeholder="API Hash" value={apiHash} onChange={e => setApiHash(e.target.value)} />
      <input placeholder="Telefone" value={phone} onChange={e => setPhone(e.target.value)} />
      {codeRequired && <input placeholder="Código recebido" value={code} onChange={e => setCode(e.target.value)} />}
      <button onClick={handleLogin}>{loading ? "Carregando..." : "Iniciar Sessão"}</button>
      {message && <p>{message}</p>}
    </div>
  );
}
