import { useEffect, useState } from "react";
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
} from "@mui/material";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid
} from "recharts";

const BACKEND = "http://localhost:8000";

export default function Charts() {
    const [mlLogs, setMlLogs] = useState<any[]>([]);

    // -------------------------------
    // Load ML logs (limit 200 rows)
    // -------------------------------
    async function loadLogs() {
        const res = await fetch(`${BACKEND}/api/logs/ml?limit=200`);
        const json = await res.json();

        // Ensure timestamps are readable
        const formatted = json.rows.map((r: any, index: number) => ({
            ...r,
            index,
            timestampLabel: new Date(r.timestamp).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            })
        }));

        setMlLogs(formatted);
    }

    useEffect(() => {
        loadLogs();
        const timer = setInterval(loadLogs, 5000);
        return () => clearInterval(timer);
    }, []);

    return (
        <Box>
            <Typography variant="h4" fontWeight={600} mb={3}>
                Energy & Environment Charts
            </Typography>

            <Grid container spacing={3}>

                {/* ----------------- CHART 1 ----------------- */}
                <Grid item xs={12} md={6}>
                    <Card sx={{ p: 2 }}>
                        <CardContent>
                            <Typography variant="h6" mb={2}>
                                House Consumption (kW) Over Time
                            </Typography>

                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={mlLogs}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="timestampLabel" />
                                    <YAxis />
                                    <Tooltip />
                                    <Line
                                        type="monotone"
                                        dataKey="house_overall_kw"
                                        stroke="#2563eb"
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* ----------------- CHART 2 ----------------- */}
                <Grid item xs={12} md={6}>
                    <Card sx={{ p: 2 }}>
                        <CardContent>
                            <Typography variant="h6" mb={2}>
                                Electricity Price (€/kWh) Over Time
                            </Typography>

                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={mlLogs}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="timestampLabel" />
                                    <YAxis />
                                    <Tooltip />
                                    <Line
                                        type="monotone"
                                        dataKey="price_eur_per_kwh"
                                        stroke="#dc2626"
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

            </Grid>
        </Box>
    );
}
