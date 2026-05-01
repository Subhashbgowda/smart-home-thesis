// src/pages/settings.tsx
import { useState, useEffect } from "react";
import {
    Box,
    Typography,
    Card,
    CardContent,
    Slider,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
    Switch,
    FormControlLabel
} from "@mui/material";

const BACKEND = "http://localhost:8000";

interface SettingsProps {
    onThemeChange: (mode: string) => void;
}

export default function Settings({ onThemeChange }: SettingsProps) {
    const [interval, setIntervalValue] = useState(1);
    const [themeMode, setThemeMode] = useState(
        localStorage.getItem("theme") || "light"
    );

    const [comfortMode, setComfortMode] = useState(false);

    // Load initial values
    useEffect(() => {
        fetch(`${BACKEND}/api/get-log-interval`)
            .then(r => r.json())
            .then(data => setIntervalValue(data.interval))
            .catch(() => { });

        fetch(`${BACKEND}/api/get-comfort-mode`)
            .then(r => r.json())
            .then(data => setComfortMode(data.comfort_mode))
            .catch(() => { });
    }, []);

    // Update interval in backend
    async function updateInterval(value: number) {
        setIntervalValue(value);
        await fetch(`${BACKEND}/api/set-log-interval`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(value)
        });
    }

    // Toggle comfort mode
    async function toggleComfort(value: boolean) {
        setComfortMode(value);
        await fetch(`${BACKEND}/api/set-comfort-mode`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(value)
        });
    }

    // Theme change
    function updateTheme(mode: string) {
        setThemeMode(mode);
        localStorage.setItem("theme", mode);
        onThemeChange(mode);
    }

    return (
        <Box>
            <Typography variant="h4" fontWeight={600} mb={3}>
                Settings
            </Typography>

            {/* THEME SELECTOR */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" mb={2}>🎨 Theme Mode</Typography>

                    <FormControl sx={{ width: 250 }}>
                        <InputLabel>Theme</InputLabel>
                        <Select
                            value={themeMode}
                            label="Theme"
                            onChange={(e) => updateTheme(e.target.value)}
                        >
                            <MenuItem value="light">Light</MenuItem>
                            <MenuItem value="dark">Dark</MenuItem>
                            <MenuItem value="blue">Blue</MenuItem>
                            <MenuItem value="green">Green</MenuItem>
                            <MenuItem value="cyberpunk">Cyberpunk</MenuItem>
                            <MenuItem value="sunset">Sunset Orange</MenuItem>
                        </Select>
                    </FormControl>
                </CardContent>
            </Card>

            {/* INTERVAL SETTING */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" mb={1}>⏱ Log Interval</Typography>
                    <Typography mb={1}>{interval} seconds</Typography>

                    <Slider
                        value={interval}
                        min={1}
                        max={120}
                        step={1}
                        onChange={(e, v) => updateInterval(v as number)}
                        sx={{ width: 300 }}
                    />
                </CardContent>
            </Card>

            {/* COMFORT MODE */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6" mb={2}>💆 Comfort Mode</Typography>

                    <FormControlLabel
                        control={
                            <Switch
                                checked={comfortMode}
                                onChange={(e) => toggleComfort(e.target.checked)}
                                color="primary"
                            />
                        }
                        label={comfortMode ? "Comfort Mode is ON" : "Comfort Mode is OFF"}
                    />
                </CardContent>
            </Card>
        </Box>
    );
}
