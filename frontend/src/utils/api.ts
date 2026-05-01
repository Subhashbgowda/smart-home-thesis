// src/utils/api.ts
const BACKEND = process.env.REACT_APP_BACKEND ?? "http://localhost:8000";

export async function getHealth() {
    return fetch(`${BACKEND}/api/health`).then(r => r.json());
}

export async function getCurrent() {
    return fetch(`${BACKEND}/api/current`).then(r => r.json());
}

export async function getRuleLatest() {
    return fetch(`${BACKEND}/api/rule-latest`).then(r => r.json());
}

export async function getMLLogs(limit = 100) {
    return fetch(`${BACKEND}/api/logs/ml?limit=${limit}`).then(r => r.json());
}

export async function getLogInterval() {
    return fetch(`${BACKEND}/api/get-log-interval`).then(r => r.json());
}

export async function setLogInterval(seconds: number) {
    // backend expects raw JSON integer body
    return fetch(`${BACKEND}/api/set-log-interval`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(seconds),
    }).then(r => r.json());
}

export async function startML() {
    return fetch(`${BACKEND}/api/start-ml`, { method: "POST" }).then(r => r.json());
}

export async function stopML() {
    return fetch(`${BACKEND}/api/stop-ml`, { method: "POST" }).then(r => r.json());
}

// ========================================================
// ⭐ NEW: COMFORT MODE API
// ========================================================

// GET comfort mode
export async function getComfortMode() {
    return fetch(`${BACKEND}/api/get-comfort-mode`).then(r => r.json());
}

// SET comfort mode (true / false)
export async function setComfortMode(enabled: boolean) {
    return fetch(`${BACKEND}/api/set-comfort-mode`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(enabled),
    }).then(r => r.json());
}
