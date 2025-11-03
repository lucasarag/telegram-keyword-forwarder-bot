"use client";
import { useState } from "react";
import { login } from "../api";

export default function LoginPage() {
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [stage, setStage] = useState<"phone" | "code">("phone");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    try {
      const result = await login(phone, stage === "code" ? code : undefined);
      setMessage(result.message);
      if (stage === "phone") setStage("code");
    } catch (err: any) {
      setMessage(err.message);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Login com Telegram</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Telefone ex: +5511999999999"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          disabled={stage === "code"}
        />
        {stage === "code" && (
          <input
            type="text"
            placeholder="Código recebido"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
        )}
        <button type="submit">
          {stage === "phone" ? "Enviar Código" : "Confirmar Código"}
        </button>
      </form>
      <p>{message}</p>
    </div>
  );
}
