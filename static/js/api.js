/**
 * Клиент API (относительные пути — тот же хост, что и у FastAPI).
 */
const API = "/api/v1";

function getToken() {
  return localStorage.getItem("ticketshop_token");
}

function setToken(token) {
  if (token) localStorage.setItem("ticketshop_token", token);
  else localStorage.removeItem("ticketshop_token");
}

const DEFAULT_FETCH_TIMEOUT_MS = 20000;

async function apiFetch(path, options = {}) {
  const { timeoutMs: optTimeoutMs, ...fetchOptions } = options;
  const headers = { ...fetchOptions.headers };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (fetchOptions.body && !(fetchOptions.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const timeoutMs = optTimeoutMs ?? DEFAULT_FETCH_TIMEOUT_MS;
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  let res;
  try {
    res = await fetch(API + path, { ...fetchOptions, headers, signal: ctrl.signal });
  } catch (e) {
    if (e.name === "AbortError") {
      throw new Error("Сервер не ответил вовремя. Проверьте, что API запущен (например, порт 8000).");
    }
    throw e;
  } finally {
    clearTimeout(t);
  }
  if (res.status === 204) return null;
  const text = await res.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    const msg = data?.detail
      ? typeof data.detail === "string"
        ? data.detail
        : JSON.stringify(data.detail)
      : res.statusText;
    const err = new Error(msg);
    err.status = res.status;
    err.body = data;
    throw err;
  }
  return data;
}

const Auth = {
  async register(email, password) {
    return apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  async login(username, password) {
    const body = new URLSearchParams();
    body.set("username", username);
    body.set("password", password);
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), DEFAULT_FETCH_TIMEOUT_MS);
    let res;
    try {
      res = await fetch(API + "/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
        signal: ctrl.signal,
      });
    } catch (e) {
      if (e.name === "AbortError") {
        throw new Error("Сервер не ответил вовремя. Проверьте, что API запущен.");
      }
      throw e;
    } finally {
      clearTimeout(t);
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);
    setToken(data.access_token);
    return data;
  },
  logout() {
    setToken(null);
  },
  async me() {
    return apiFetch("/auth/me");
  },
  async patchMe(payload) {
    return apiFetch("/auth/me", { method: "PATCH", body: JSON.stringify(payload) });
  },
};

const Concerts = {
  list(limit = 100, offset = 0) {
    return apiFetch(`/concerts/?limit=${limit}&offset=${offset}`);
  },
  get(id) {
    return apiFetch(`/concerts/${id}`);
  },
  purchaseOptions(id) {
    return apiFetch(`/concerts/${id}/purchase-options`);
  },
  groups(id) {
    return apiFetch(`/concerts/${id}/groups`);
  },
  addGroup(concertId, groupId) {
    return apiFetch(`/concerts/${concertId}/groups/${groupId}`, { method: "POST" });
  },
  removeGroup(concertId, groupId) {
    return apiFetch(`/concerts/${concertId}/groups/${groupId}`, { method: "DELETE" });
  },
  create(payload) {
    return apiFetch("/concerts/", { method: "POST", body: JSON.stringify(payload) });
  },
  update(id, payload) {
    return apiFetch(`/concerts/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
  },
  delete(id) {
    return apiFetch(`/concerts/${id}`, { method: "DELETE" });
  },
};

const Halls = {
  list() {
    return apiFetch("/halls/?limit=200&offset=0");
  },
  create(payload) {
    return apiFetch("/halls/", { method: "POST", body: JSON.stringify(payload) });
  },
  update(id, payload) {
    return apiFetch(`/halls/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
  },
  delete(id) {
    return apiFetch(`/halls/${id}`, { method: "DELETE" });
  },
};

const Groups = {
  list() {
    return apiFetch("/groups/?limit=200&offset=0");
  },
  create(payload) {
    return apiFetch("/groups/", { method: "POST", body: JSON.stringify(payload) });
  },
  update(id, payload) {
    return apiFetch(`/groups/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
  },
  delete(id) {
    return apiFetch(`/groups/${id}`, { method: "DELETE" });
  },
};

const Sales = {
  buy(payload) {
    return apiFetch("/sales/buy", { method: "POST", body: JSON.stringify(payload) });
  },
  // Новый метод для админа
  recent_sales() {
    return apiFetch("/admin/sales/recent");
  },
  delete(id) {
    return apiFetch(`/sales/${id}`, { method: "DELETE" });
  }
};

const Watchlist = {
  list() {
    return apiFetch("/watchlist/");
  },
  add(concertId) {
    return apiFetch(`/watchlist/${concertId}`, { method: "POST" });
  },
  remove(concertId) {
    return apiFetch(`/watchlist/${concertId}`, { method: "DELETE" });
  },
  status(concertId) {
    return apiFetch(`/watchlist/${concertId}/status`);
  },
};

const Admin = {
  recentSales(limit = 50) {
    return apiFetch(`/admin/sales/recent?limit=${limit}&offset=0`);
  },
};

window.TicketshopApi = { Auth, Concerts, Halls, Groups, Sales, Watchlist, Admin, getToken, setToken };
