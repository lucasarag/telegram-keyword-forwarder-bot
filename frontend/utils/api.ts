export const API_TOKEN = process.env.NEXT_PUBLIC_API_TOKEN || "";
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function login(api_id: number, api_hash: string, phone: string, code?: string) {
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-api-token": API_TOKEN },
    body: JSON.stringify({ api_id, api_hash, phone, code }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function setConfig(keyword: string, chat_id: number) {
  const res = await fetch(`${API_URL}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-api-token": API_TOKEN },
    body: JSON.stringify({ keyword, chat_id }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function startForward() {
  const res = await fetch(`${API_URL}/start`, { method: "POST", headers: { "x-api-token": API_TOKEN } });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function stopForward() {
  const res = await fetch(`${API_URL}/stop`, { method: "POST", headers: { "x-api-token": API_TOKEN } });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getLogs(limit = 50) {
  const res = await fetch(`${API_URL}/logs?limit=${limit}`, { headers: { "x-api-token": API_TOKEN } });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
