// src/pages/Dashboard.tsx

import React, { useEffect, useRef, useState } from "react";
import {
    Box,
    Card,
    CardContent,
    Typography,
    Chip,
    Button,
    Grid,
    IconButton,
    Tooltip,
    Avatar,
    Switch,
    FormControlLabel,
    useTheme
} from "@mui/material";

import PowerIcon from "@mui/icons-material/PowerSettingsNew";
import ThermostatIcon from "@mui/icons-material/Thermostat";
import PriceChangeIcon from "@mui/icons-material/PriceChange";
import HomeIcon from "@mui/icons-material/Home";
import WbSunnyIcon from "@mui/icons-material/WbSunny";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";

import { getCurrentUser, logoutUser } from "../utils/auth";

const BACKEND = "http://127.0.0.1:8000";

export default function Dashboard(): React.ReactElement {
    const theme = useTheme();
    const user = getCurrentUser();

    // --------------------- STATE ---------------------
    const [backendStatus, setBackendStatus] = useState<"loading" | "ok" | "error">("loading");
    const [data, setData] = useState<any>(null);
    const [isRunning, setIsRunning] = useState(false);
    const [logInterval, setLogInterval] = useState<number>(1);
    const [muted, setMuted] = useState(true);
    const [comfortMode, setComfortMode] = useState(false);

    // Weather sound refs
    const rainAudio = useRef<HTMLAudioElement | null>(null);
    const thunderAudio = useRef<HTMLAudioElement | null>(null);
    const windAudio = useRef<HTMLAudioElement | null>(null);
    const snowAudio = useRef<HTMLAudioElement | null>(null);

    // --------------------- LOAD BACKEND DATA ---------------------
    async function loadData() {
        try {
            const health = await fetch(`${BACKEND}/api/health`).then(r => r.json());
            setBackendStatus(health?.status === "ok" ? "ok" : "error");

            const current = await fetch(`${BACKEND}/api/current`).then(r => r.json());
            setData(current);

            const intv = await fetch(`${BACKEND}/api/get-log-interval`).then(r => r.json());
            if (typeof intv?.interval === "number") setLogInterval(intv.interval);

            const comfort = await fetch(`${BACKEND}/api/get-comfort-mode`).then(r => r.json());
            setComfortMode(comfort.comfort_mode);
        } catch {
            setBackendStatus("error");
        }
    }

    useEffect(() => {
        loadData();
        const timer = setInterval(loadData, logInterval * 1000);
        return () => clearInterval(timer);
    }, [logInterval]);

    // --------------------- COMFORT MODE ---------------------
    async function toggleComfortMode() {
        const newValue = !comfortMode;
        setComfortMode(newValue);

        await fetch(`${BACKEND}/api/set-comfort-mode`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newValue)
        });
    }

    // --------------------- START/STOP ML ---------------------
    async function startML() {
        console.log("START FUNCTION CALLED");

        try {
            const res = await fetch("http://127.0.0.1:8000/api/start-ml", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            });

            console.log("FETCH SENT");

            const data = await res.json();
            console.log("RESPONSE:", data);

            if (data?.status === "started" || data?.status === "already_running") {
                setIsRunning(true);
            }

        } catch (err) {
            console.error("FETCH ERROR:", err);
        }
    }

    async function stopML() {
        try {
            const res = await fetch(`${BACKEND}/api/stop-ml`, { method: "POST" }).then(r => r.json());
            if (res?.status === "stopped" || res?.status === "not_running") setIsRunning(false);
        } catch { }
    }

    // --------------------- BULB STATE WITH COMFORT MODE ---------------------
    const bulbOn = comfortMode ? true : (
        data?.latest?.action &&
        !data.latest.action.toLowerCase().includes("turn off")
    );

    // --------------------- WEATHER SOUND LOGIC ---------------------
    function getWeatherType(condition: string | undefined) {
        if (!condition) return "clear";
        const s = condition.toLowerCase();
        if (s.includes("snow")) return "snow";
        if (s.includes("storm") || s.includes("thunder")) return "storm";
        if (s.includes("rain") || s.includes("drizzle")) return "rain";
        if (s.includes("fog") || s.includes("mist")) return "fog";
        if (s.includes("cloud")) return "cloud";
        return "sun";
    }

    const weatherType = getWeatherType(data?.latest?.condition);

    useEffect(() => {
        const init = (ref: any, src: string) => {
            ref.current = new Audio(src);
            ref.current.loop = true;
            ref.current.muted = true;
        };

        init(rainAudio, "/sounds/rain.mp3");
        init(thunderAudio, "/sounds/thunder.mp3");
        init(windAudio, "/sounds/wind.mp3");
        init(snowAudio, "/sounds/snow.mp3");

        return () => {
            rainAudio.current?.pause();
            thunderAudio.current?.pause();
            windAudio.current?.pause();
            snowAudio.current?.pause();
        };
    }, []);

    useEffect(() => {
        if (muted) {
            [rainAudio, thunderAudio, windAudio, snowAudio].forEach(a => a.current?.pause());
            return;
        }

        [rainAudio, thunderAudio, windAudio, snowAudio].forEach(a => a.current?.pause());

        if (weatherType === "rain") rainAudio.current?.play();
        if (weatherType === "storm") {
            rainAudio.current?.play();
            thunderAudio.current?.play();
        }
        if (weatherType === "snow") snowAudio.current?.play();
        if (weatherType === "cloud" || weatherType === "fog") windAudio.current?.play();
    }, [weatherType, muted]);

    // --------------------- SMALL CARD COMPONENT ---------------------
    const InfoCard = ({ icon, title, value }: any) => (
        <Card
            className="glow-card"
            sx={{
                borderRadius: 2,
                background: theme.palette.mode === "dark" ? "#1e293b" : "#ffffff",
                transition: "0.3s"
            }}
        >
            <CardContent sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Box sx={{ opacity: 0.8 }}>{icon}</Box>
                <Box>
                    <Typography variant="caption" color="text.secondary">
                        {title}
                    </Typography>
                    <Typography fontSize={17} fontWeight={600}>
                        {value}
                    </Typography>
                </Box>
            </CardContent>
        </Card>
    );

    const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

    // --------------------- MAIN UI ---------------------
    return (
        <Box
            className={bulbOn ? "ambient-glow" : ""}
            sx={{
                p: 2,
                minHeight: "100%",
                background: theme.palette.mode === "dark" ? "#0f172a" : "#f2f4f7",
                transition: "0.4s"
            }}
        >

            {/* -------- USER BAR -------- */}
            <Box
                sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    p: 2,
                    mb: 3,
                    borderRadius: 2,
                    background: theme.palette.mode === "dark" ? "#1e293b" : "#ffffff",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
                }}
            >
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                    <Avatar src={user?.photo || ""} sx={{ width: 48, height: 48 }} />

                    <Box>
                        <Typography variant="h6" fontWeight={600}>
                            👋 Hello, {user?.name || "User"}
                        </Typography>
                        <Typography color="text.secondary">{user?.email}</Typography>
                    </Box>
                </Box>

                <Button variant="outlined" color="error" onClick={logoutUser}>
                    Logout
                </Button>
            </Box>

            {/* -------- COMFORT MODE -------- */}
            <Box
                sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 2,
                    mb: 3,
                    p: 2,
                    borderRadius: 2,
                    background: theme.palette.mode === "dark" ? "#1e293b" : "#ffffff",
                    boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
                }}
            >
                <FormControlLabel
                    control={
                        <Switch
                            checked={comfortMode}
                            onChange={toggleComfortMode}
                            color="primary"
                        />
                    }
                    label={comfortMode ? "Comfort Mode: ON" : "Comfort Mode: OFF"}
                />
            </Box>

            {/* -------- DASH HEADER -------- */}
            <Box display="flex" justifyContent="space-between" mb={3}>
                <Box>
                    <Typography variant="h5" fontWeight={700}>
                        Smart Home Dashboard
                    </Typography>
                    <Chip
                        label={`Backend: ${backendStatus.toUpperCase()}`}
                        color={backendStatus === "ok" ? "success" : "error"}
                        sx={{ mt: 1 }}
                    />
                </Box>

                <Box display="flex" gap={1} alignItems="center">
                    <Tooltip title={muted ? "Unmute ambient sound" : "Mute ambient sound"}>
                        <IconButton onClick={() => setMuted(m => !m)}>
                            {muted ? <VolumeOffIcon /> : <VolumeUpIcon />}
                        </IconButton>
                    </Tooltip>
                    <Button
                        variant="contained"
                        color="success"
                        onClick={startML}
                    >
                        Start
                    </Button>
                    <Button variant="contained" color="error" onClick={stopML}>Stop</Button>
                </Box>
            </Box>

            {/* -------- INTERVAL SELECTOR -------- */}
            <Box display="flex" gap={2} mb={3}>
                <Typography fontWeight={600}>Logging Interval:</Typography>

                <select
                    value={logInterval}
                    onChange={async (e) => {
                        const seconds = Number(e.target.value);
                        setLogInterval(seconds);

                        await fetch(`${BACKEND}/api/set-log-interval`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(seconds),
                        });
                    }}
                    style={{
                        padding: "6px 10px",
                        fontSize: 14,
                        borderRadius: 6,
                        border: "1px solid #ccc",
                    }}
                >
                    <option value={1}>1 sec</option>
                    <option value={5}>5 sec</option>
                    <option value={10}>10 sec</option>
                    <option value={30}>30 sec</option>
                    <option value={60}>1 minute</option>
                    <option value={600}>10 minutes</option>
                </select>
            </Box>

            {/* -------- MAIN DATA GRID -------- */}
            {!data ? (
                <Typography>Loading...</Typography>
            ) : (
                <Grid container spacing={2}>

                    <Grid item xs={6} md={3}>
                        <InfoCard icon={<PowerIcon fontSize="small" />} title="Consumption" value={`${(data?.latest?.house_overall_kw ?? 0).toFixed(2)} kW`} />
                    </Grid>

                    <Grid item xs={6} md={3}>
                        <InfoCard icon={<ThermostatIcon fontSize="small" />} title="Temperature" value={`${data?.latest?.temperature ?? "-"} °C`} />
                    </Grid>

                    <Grid item xs={6} md={3}>
                        <InfoCard icon={<PriceChangeIcon fontSize="small" />} title="Price" value={`€ ${data?.latest?.price_eur_per_kwh ?? "-"}`} />
                    </Grid>

                    <Grid item xs={6} md={3}>
                        <InfoCard icon={<WbSunnyIcon fontSize="small" />} title="Humidity" value={`${data?.latest?.humidity ?? "-"}%`} />
                    </Grid>

                    <Grid item xs={6} md={3}>
                        <InfoCard icon={<WbSunnyIcon fontSize="small" />} title="Condition" value={data?.latest?.condition ?? "-"} />
                    </Grid>

                    <Grid item xs={6} md={3}>
                        <InfoCard icon={<HomeIcon fontSize="small" />} title="Occupancy" value={comfortMode ? "FORCE ON" : (data?.latest?.occupied ? "Occupied" : "Empty")} />
                    </Grid>

                    <Grid item xs={6} md={3}>
                        <InfoCard title="Time" value={`${data?.latest?.hour_of_day ?? "--"}:00 (${dayNames[data?.latest?.day_of_week ?? 0]})`} />
                    </Grid>

                    <Grid item xs={6} md={3}>
                        <InfoCard title="Last Update" value={data?.latest?.timestamp ? new Date(data.latest.timestamp).toLocaleString() : "-"} />
                    </Grid>

                    {/* Smart Light */}
                    <Grid item xs={12} md={4}>
                        <Card
                            className="glow-card"
                            sx={{
                                borderRadius: 2,
                                background: bulbOn ? "#fff8b3" : "#ffffff",
                                transition: "0.4s",
                            }}
                        >
                            <CardContent sx={{ display: "flex", gap: 2 }}>
                                <LightbulbIcon
                                    sx={{
                                        fontSize: 50,
                                        color: bulbOn ? "#ffe100" : "#9e9e9e",
                                    }}
                                />
                                <Box>
                                    <Typography fontWeight={600}>Smart Light</Typography>
                                    <Typography fontSize={20} fontWeight={700}>
                                        {bulbOn ? "ON" : "OFF"}
                                    </Typography>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* AI ACTION */}
                    <Grid item xs={12} md={8}>
                        <Card
                            className="glow-card"
                            sx={{
                                borderRadius: 2,
                                background: theme.palette.mode === "dark" ? "#1e293b" : "#ffffff",
                            }}
                        >
                            <CardContent>
                                <Typography variant="subtitle1" fontWeight={600}>AI Action</Typography>
                                <Typography fontSize={20} fontWeight={700}>
                                    {comfortMode ? "COMFORT MODE OVERRIDE" : data?.latest?.action ?? "-"}
                                </Typography>
                                {!comfortMode && (
                                    <Typography>
                                        Confidence:{" "}
                                        {data?.latest?.confidence
                                            ? (data.latest.confidence * 100).toFixed(1) + "%"
                                            : "-"}
                                    </Typography>
                                )}
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {/* Stronger Glow CSS */}
            <style>{`
                .ambient-glow {
                    box-shadow: inset 0 0 180px rgba(255, 223, 61, 0.40);
                }
                .ambient-glow .glow-card {
                    box-shadow: 0 0 45px rgba(255, 235, 59, 1.0) !important;
                    transition: box-shadow 0.4s ease-in-out, transform 0.4s ease-in-out;
                }
                .glow-card:hover {
                    transform: translateY(-3px);
                }
            `}</style>
        </Box>
    );
}
