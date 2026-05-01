const BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";

export async function fetchHealth() {
    const res = await fetch(`${BASE_URL}/api/health`);
    return res.json();
}

export async function fetchCurrent() {
    const res = await fetch(`${BASE_URL}/api/current`);
    return res.json();
}
