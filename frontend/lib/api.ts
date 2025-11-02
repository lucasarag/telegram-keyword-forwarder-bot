const BASE_URL = process.env.NEXT_PUBLIC_API_URL;
const TOKEN = process.env.NEXT_PUBLIC_API_TOKEN;

const request = async (path: string, data?: any, method = "GET") => {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      "x-api-token": TOKEN,
    },
    body: data ? JSON.stringify(data) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const api = {
  login: (data: any) => request("/login", data, "POST"),
  config: (data: any) => request("/config", data, "POST"),
  start: () => request("/start", undefined, "POST"),
  stop: () => request("/stop", undefined, "POST"),
  getLogs: () => request("/logs"),
  getStatus: () => request("/status"),
};
