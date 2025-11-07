export async function login(apiId: number, apiHash: string, phone: string, code?: string) {
  const response = await fetch("http://localhost:8000/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ apiId, apiHash, phone, code }),
  });
  if (!response.ok) throw new Error(await response.text());
  return await response.json();
}
